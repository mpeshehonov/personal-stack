"use client";

import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";

type Props = {
  locale: Locale;
  dict: Dictionary;
};

export function ResumeHeaderActions({ locale, dict }: Props) {
  const printLabel = locale === "en" ? "Print" : "Печать";

  return (
    <div className="flex shrink-0 flex-wrap gap-3">
      <a
        href={localizedPath(locale, "/resume/download")}
        className="btn-primary"
      >
        {dict.resume.download}
      </a>
      <button
        type="button"
        onClick={() => typeof window !== "undefined" && window.print()}
        className="btn-secondary print:hidden"
      >
        {printLabel}
      </button>
    </div>
  );
}
