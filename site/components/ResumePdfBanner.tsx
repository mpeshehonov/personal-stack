"use client";

import type { Locale } from "@/middleware";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";

type Props = {
  locale: Locale;
  dict: Dictionary;
};

export function ResumePdfBanner({ locale, dict }: Props) {
  const printLabel = locale === "en" ? "Print-friendly page" : "Версия для печати";

  return (
    <div className="resume-pdf-banner mb-8 rounded-2xl border border-accent/30 bg-gradient-to-r from-accent-soft to-surface p-5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-mono text-xs font-semibold uppercase tracking-widest text-accent">
            {dict.resume.title}
          </p>
          <p className="mt-1 text-sm text-ink-muted">{dict.resume.downloadHint}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <a
            href={localizedPath(locale, "/resume/download")}
            className="btn-primary"
            download
          >
            {dict.resume.download}
            <span aria-hidden>↓</span>
          </a>
          <button
            type="button"
            onClick={() => typeof window !== "undefined" && window.print()}
            className="btn-secondary print:hidden"
          >
            {printLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
