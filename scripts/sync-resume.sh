#!/usr/bin/env bash
# Sync main resume from ~/personal/cv into the site
set -euo pipefail

CV_DIR="${CV_DIR:-$HOME/personal/cv}"
SITE_DIR="$(cd "$(dirname "$0")/../site" && pwd)"

echo "==> Building PDF in $CV_DIR"
make -C "$CV_DIR" resume-main

echo "==> Copying markdown and PDF to site"
cp "$CV_DIR/resume_main_ru.md" "$SITE_DIR/content/resume/resume.md"
cp "$CV_DIR/dist/resume_main_ru.pdf" "$SITE_DIR/public/Maksim_Peshekhonov_CV.pdf"

echo "==> Done"
ls -la "$SITE_DIR/public/Maksim_Peshekhonov_CV.pdf"
