import { createReadStream } from "fs";
import { access } from "fs/promises";
import path from "path";
import {
  bundlePath,
  listOrders,
  verifyDeliveryToken,
} from "@/lib/a4-checkout";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const token = new URL(request.url).searchParams.get("token");
  if (!token) {
    return NextResponse.json({ error: "missing_token" }, { status: 400 });
  }

  const orders = await listOrders();
  const order = orders.find(
    (o) => o.status === "fulfilled" && verifyDeliveryToken(o, token),
  );
  if (!order) {
    return NextResponse.json({ error: "invalid_or_expired_token" }, { status: 403 });
  }

  const filePath = bundlePath();
  try {
    await access(filePath);
  } catch {
    return NextResponse.json({ error: "bundle_unavailable" }, { status: 503 });
  }

  const fileName = path.basename(filePath);
  const stream = createReadStream(filePath);
  return new NextResponse(stream as unknown as BodyInit, {
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Disposition": `attachment; filename="${fileName}"`,
      "Cache-Control": "no-store",
    },
  });
}
