import crypto from "crypto";
import fs from "fs/promises";
import path from "path";

export type CheckoutProvider = "nowpayments" | "cryptomus";

export type CheckoutOrder = {
  order_id: string;
  payment_id: string;
  provider: CheckoutProvider;
  status: "pending" | "fulfilled" | "failed";
  pay_amount?: number;
  pay_currency?: string;
  price_usd: number;
  net_usd: number;
  delivery_token?: string;
  delivery_expires?: string;
  fulfilled_at?: string;
  synced_finance: boolean;
};

type OrdersFile = {
  orders: CheckoutOrder[];
};

const DATA_DIR = process.env.CHECKOUT_DATA_DIR || "/app/data/checkout";
const ORDERS_PATH =
  process.env.CHECKOUT_ORDERS_PATH || path.join(DATA_DIR, "orders.json");
const DELIVERY_SECRET = process.env.CHECKOUT_DELIVERY_SECRET || "";
const NOWPAYMENTS_IPN_SECRET = process.env.NOWPAYMENTS_IPN_SECRET || "";
const CRYPTOMUS_API_KEY = process.env.CRYPTOMUS_API_KEY || "";
const BUNDLE_PATH =
  process.env.A4_BUNDLE_PATH ||
  "/app/delivery/personal-stack-agent-starter-v0.3.tar.gz";
const INTRO_PRICE_USD = Number(process.env.A4_INTRO_PRICE_USD || "19");
const REGULAR_PRICE_USD = Number(process.env.A4_REGULAR_PRICE_USD || "29");
const DELIVERY_TTL_DAYS = Number(process.env.CHECKOUT_DELIVERY_TTL_DAYS || "7");
const FEE_RATE = Number(process.env.CHECKOUT_FEE_RATE || "0.01");

export function checkoutConfigured(): boolean {
  return Boolean(DELIVERY_SECRET && (NOWPAYMENTS_IPN_SECRET || CRYPTOMUS_API_KEY));
}

export function bundlePath(): string {
  return BUNDLE_PATH;
}

export function expectedPriceUsd(orderCount: number): number {
  return orderCount < 20 ? INTRO_PRICE_USD : REGULAR_PRICE_USD;
}

function sortObjectKeys(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sortObjectKeys);
  }
  if (value && typeof value === "object") {
    const obj = value as Record<string, unknown>;
    return Object.keys(obj)
      .sort()
      .reduce<Record<string, unknown>>((acc, key) => {
        acc[key] = sortObjectKeys(obj[key]);
        return acc;
      }, {});
  }
  return value;
}

export function verifyNowpaymentsSignature(
  body: Record<string, unknown>,
  signature: string | null,
): boolean {
  if (!NOWPAYMENTS_IPN_SECRET || !signature) {
    return false;
  }
  const payload = JSON.stringify(sortObjectKeys(body));
  const expected = crypto
    .createHmac("sha512", NOWPAYMENTS_IPN_SECRET)
    .update(payload)
    .digest("hex");
  const a = Buffer.from(expected, "hex");
  const b = Buffer.from(signature, "hex");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

export function verifyCryptomusSignature(
  body: Record<string, unknown>,
  sign: string | null,
): boolean {
  if (!CRYPTOMUS_API_KEY || !sign) {
    return false;
  }
  const encoded = Buffer.from(JSON.stringify(body)).toString("base64");
  const expected = crypto
    .createHash("md5")
    .update(encoded + CRYPTOMUS_API_KEY)
    .digest("hex");
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(sign));
}

function deliveryToken(orderId: string, paymentId: string, expiresAt: string): string {
  const payload = `${orderId}:${paymentId}:${expiresAt}`;
  return crypto
    .createHmac("sha256", DELIVERY_SECRET)
    .update(payload)
    .digest("hex");
}

export function verifyDeliveryToken(
  order: CheckoutOrder,
  token: string,
): boolean {
  if (!order.delivery_token || !order.delivery_expires) {
    return false;
  }
  if (new Date(order.delivery_expires).getTime() < Date.now()) {
    return false;
  }
  const a = Buffer.from(order.delivery_token);
  const b = Buffer.from(token);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

async function readOrders(): Promise<OrdersFile> {
  try {
    const raw = await fs.readFile(ORDERS_PATH, "utf-8");
    const data = JSON.parse(raw) as Partial<OrdersFile>;
    return { orders: Array.isArray(data.orders) ? data.orders : [] };
  } catch {
    return { orders: [] };
  }
}

async function writeOrders(data: OrdersFile): Promise<void> {
  await fs.mkdir(path.dirname(ORDERS_PATH), { recursive: true });
  await fs.writeFile(ORDERS_PATH, JSON.stringify(data, null, 2), "utf-8");
}

export async function listOrders(): Promise<CheckoutOrder[]> {
  const data = await readOrders();
  return data.orders;
}

export async function findOrderByPaymentId(
  paymentId: string,
): Promise<CheckoutOrder | undefined> {
  const data = await readOrders();
  return data.orders.find((o) => o.payment_id === paymentId);
}

export async function fulfillNowpaymentsOrder(
  body: Record<string, unknown>,
): Promise<CheckoutOrder | null> {
  const paymentId = String(body.payment_id || body.order_id || "");
  const paymentStatus = String(body.payment_status || "");
  if (!paymentId) {
    return null;
  }

  const data = await readOrders();
  const fulfilledCount = data.orders.filter((o) => o.status === "fulfilled").length;
  const priceUsd = Number(body.price_amount || expectedPriceUsd(fulfilledCount));
  const netUsd = Math.round(priceUsd * (1 - FEE_RATE) * 100) / 100;

  let order = data.orders.find((o) => o.payment_id === paymentId);
  if (!order) {
    order = {
      order_id: `NP-${paymentId}`,
      payment_id: paymentId,
      provider: "nowpayments",
      status: "pending",
      pay_amount: Number(body.pay_amount || 0),
      pay_currency: String(body.pay_currency || "usdt"),
      price_usd: priceUsd,
      net_usd: netUsd,
      synced_finance: false,
    };
    data.orders.push(order);
  }

  if (paymentStatus === "finished" || paymentStatus === "confirmed") {
    const expiresAt = new Date(
      Date.now() + DELIVERY_TTL_DAYS * 24 * 60 * 60 * 1000,
    ).toISOString();
    order.status = "fulfilled";
    order.fulfilled_at = new Date().toISOString();
    order.delivery_expires = expiresAt;
    order.delivery_token = deliveryToken(order.order_id, paymentId, expiresAt);
    order.price_usd = priceUsd;
    order.net_usd = netUsd;
  } else if (
    paymentStatus === "failed" ||
    paymentStatus === "refunded" ||
    paymentStatus === "expired"
  ) {
    order.status = "failed";
  }

  await writeOrders(data);
  return order.status === "fulfilled" ? order : null;
}

export async function fulfillCryptomusOrder(
  body: Record<string, unknown>,
): Promise<CheckoutOrder | null> {
  const paymentId = String(body.uuid || body.order_id || "");
  const paymentStatus = String(body.payment_status || body.status || "");
  if (!paymentId) {
    return null;
  }

  const data = await readOrders();
  const fulfilledCount = data.orders.filter((o) => o.status === "fulfilled").length;
  const priceUsd = Number(body.amount || expectedPriceUsd(fulfilledCount));
  const netUsd = Math.round(priceUsd * (1 - FEE_RATE) * 100) / 100;

  let order = data.orders.find((o) => o.payment_id === paymentId);
  if (!order) {
    order = {
      order_id: `CM-${paymentId}`,
      payment_id: paymentId,
      provider: "cryptomus",
      status: "pending",
      pay_currency: String(body.currency || "USDT"),
      price_usd: priceUsd,
      net_usd: netUsd,
      synced_finance: false,
    };
    data.orders.push(order);
  }

  if (paymentStatus === "paid" || paymentStatus === "paid_over") {
    const expiresAt = new Date(
      Date.now() + DELIVERY_TTL_DAYS * 24 * 60 * 60 * 1000,
    ).toISOString();
    order.status = "fulfilled";
    order.fulfilled_at = new Date().toISOString();
    order.delivery_expires = expiresAt;
    order.delivery_token = deliveryToken(order.order_id, paymentId, expiresAt);
    order.price_usd = priceUsd;
    order.net_usd = netUsd;
  } else if (paymentStatus === "cancel" || paymentStatus === "fail") {
    order.status = "failed";
  }

  await writeOrders(data);
  return order.status === "fulfilled" ? order : null;
}

export async function markOrderSynced(orderId: string): Promise<void> {
  const data = await readOrders();
  const order = data.orders.find((o) => o.order_id === orderId);
  if (order) {
    order.synced_finance = true;
    await writeOrders(data);
  }
}
