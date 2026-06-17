import { getVisitCount, incrementVisitCount } from "@/lib/visit-counter";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const count = await getVisitCount();
  return NextResponse.json({ count });
}

export async function POST() {
  const count = await incrementVisitCount();
  return NextResponse.json({ count });
}
