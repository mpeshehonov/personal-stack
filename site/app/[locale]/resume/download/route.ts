import { readFile } from "fs/promises";
import path from "path";
import { NextResponse } from "next/server";
import { pdfByLocale } from "@/lib/i18n";
import type { Locale } from "@/middleware";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ locale: string }> },
) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const { file, downloadName } = pdfByLocale[locale];
  const pdfPath = path.join(process.cwd(), "public", file);

  try {
    const buffer = await readFile(pdfPath);
    return new NextResponse(buffer, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="${downloadName}"`,
      },
    });
  } catch {
    return NextResponse.json(
      {
        error: `PDF not found (${file}). Run scripts/sync-resume.sh from ~/personal/cv.`,
      },
      { status: 404 },
    );
  }
}
