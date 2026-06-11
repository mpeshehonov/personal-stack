import { readFile } from "fs/promises";
import path from "path";
import { NextResponse } from "next/server";

export async function GET() {
  const pdfPath = path.join(process.cwd(), "public", "Maksim_Peshekhonov_CV.pdf");

  try {
    const buffer = await readFile(pdfPath);
    return new NextResponse(buffer, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": 'attachment; filename="Maksim_Peshekhonov_CV.pdf"',
      },
    });
  } catch {
    return NextResponse.json(
      { error: "PDF not found. Sync from ~/personal/cv with make resume-main." },
      { status: 404 },
    );
  }
}
