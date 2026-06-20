#!/usr/bin/env bash
# Build RU/EN resume markdown from site/resume-data.ts and PDFs via ~/personal/cv.
# PDF = main version only (5 employers through Citilink; older projects stay on /projects).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CV_DIR="${CV_DIR:-$HOME/personal/cv}"
SITE="$ROOT/site"

if [[ ! -d "$CV_DIR" ]]; then
  echo "CV repo not found: $CV_DIR (set CV_DIR=...)" >&2
  exit 1
fi

echo "==> Export resume markdown from resume-data.ts"
cd "$SITE"
node scripts/export-resume-md.mjs

echo "==> Sync main resume sources to $CV_DIR"
cp content/resume/resume.md "$CV_DIR/resume_main_ru.md"
cp content/resume/en/resume.md "$CV_DIR/resume_main_en.md"

echo "==> Build PDFs (resume-main = without projects section)"
make -C "$CV_DIR" resume-main

echo "==> Copy PDFs into site/public"
cp "$CV_DIR/dist/resume_main_ru.pdf" "$SITE/public/Maksim_Peshekhonov_CV_RU.pdf"
cp "$CV_DIR/dist/resume_main_en.pdf" "$SITE/public/Maksim_Peshekhonov_CV_EN.pdf"

ls -la "$SITE/public/Maksim_Peshekhonov_CV_"*.pdf
echo "==> Done"
