#!/usr/bin/env bash
# Sync resumes from ~/personal/cv into the site (RU + EN PDFs)
set -euo pipefail

CV_DIR="${CV_DIR:-$HOME/personal/cv}"
SITE_DIR="$(cd "$(dirname "$0")/../site" && pwd)"

echo "==> Building PDFs in $CV_DIR"
make -C "$CV_DIR" resume-main

echo "==> Copying RU markdown and PDF"
cp "$CV_DIR/resume_main_ru.md" "$SITE_DIR/content/resume/resume.md"
cp "$CV_DIR/dist/resume_main_ru.pdf" "$SITE_DIR/public/Maksim_Peshekhonov_CV_RU.pdf"

echo "==> Copying EN markdown and PDF"
cp "$CV_DIR/resume_main_en.md" "$SITE_DIR/content/resume/en/resume.md"
cp "$CV_DIR/dist/resume_main_en.pdf" "$SITE_DIR/public/Maksim_Peshekhonov_CV_EN.pdf"

echo "==> Done"
ls -la "$SITE_DIR/public/Maksim_Peshekhonov_CV_"*.pdf
