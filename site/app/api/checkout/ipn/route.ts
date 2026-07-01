import {
  checkoutConfigured,
  fulfillCryptomusOrder,
  fulfillNowpaymentsOrder,
  verifyCryptomusSignature,
  verifyNowpaymentsSignature,
} from "@/lib/a4-checkout";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function providerFromRequest(
  request: Request,
  body: Record<string, unknown>,
): "nowpayments" | "cryptomus" | null {
  const header = request.headers.get("x-nowpayments-sig");
  if (header) {
    return "nowpayments";
  }
  if (body.sign && (body.uuid || body.order_id)) {
    return "cryptomus";
  }
  const q = new URL(request.url).searchParams.get("provider");
  if (q === "cryptomus" || q === "nowpayments") {
    return q;
  }
  return null;
}

export async function POST(request: Request) {
  if (!checkoutConfigured()) {
    return NextResponse.json(
      { error: "checkout_not_configured" },
      { status: 503 },
    );
  }

  let body: Record<string, unknown>;
  try {
    body = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "invalid_json" }, { status: 400 });
  }

  const provider = providerFromRequest(request, body);
  if (!provider) {
    return NextResponse.json({ error: "unknown_provider" }, { status: 400 });
  }

  if (provider === "nowpayments") {
    const sig = request.headers.get("x-nowpayments-sig");
    if (!verifyNowpaymentsSignature(body, sig)) {
      return NextResponse.json({ error: "invalid_signature" }, { status: 401 });
    }
    const order = await fulfillNowpaymentsOrder(body);
    if (!order) {
      return NextResponse.json({ status: "acknowledged" });
    }
    const base = process.env.CHECKOUT_PUBLIC_BASE_URL || "https://mpeshekhonov.ru";
    return NextResponse.json({
      status: "fulfilled",
      order_id: order.order_id,
      delivery_url: `${base}/api/checkout/delivery?token=${order.delivery_token}`,
      expires_at: order.delivery_expires,
    });
  }

  const sign = typeof body.sign === "string" ? body.sign : null;
  const { sign: _ignored, ...payload } = body;
  if (!verifyCryptomusSignature(payload, sign)) {
    return NextResponse.json({ error: "invalid_signature" }, { status: 401 });
  }
  const order = await fulfillCryptomusOrder(payload);
  if (!order) {
    return NextResponse.json({ status: "acknowledged" });
  }
  const base = process.env.CHECKOUT_PUBLIC_BASE_URL || "https://mpeshekhonov.ru";
  return NextResponse.json({
    status: "fulfilled",
    order_id: order.order_id,
    delivery_url: `${base}/api/checkout/delivery?token=${order.delivery_token}`,
    expires_at: order.delivery_expires,
  });
}

export async function GET() {
  return NextResponse.json({
    service: "a4-checkout-ipn",
    configured: checkoutConfigured(),
    providers: ["nowpayments", "cryptomus"],
  });
}
