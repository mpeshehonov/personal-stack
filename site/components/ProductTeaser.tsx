import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import { FadeIn } from "./FadeIn";

type Props = {
  locale: Locale;
  dict: Dictionary;
};

export function ProductTeaser({ locale, dict }: Props) {
  return (
    <FadeIn className="section">
      <div className="card relative overflow-hidden border-0 bg-gradient-to-br from-surface via-surface to-accent-soft p-8 sm:p-10">
        <div
          className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-accent/10 blur-3xl"
          aria-hidden
        />
        <div className="relative">
          <p className="section-label">{dict.sections.productTeaser}</p>
          <h2 className="section-title mb-2">{dict.sections.productTitle}</h2>
          <p className="mb-6 max-w-2xl text-ink-muted">{dict.sections.productTeaserDesc}</p>
          <div className="flex flex-wrap gap-3">
            <Link
              href={localizedPath(locale, "/blog/self-hosted-agent-stack")}
              className="btn-primary"
            >
              {dict.sections.productTeaserCta}
            </Link>
            <a
              href="https://t.me/makusimu_san"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              {dict.sections.productTeaserEarlyAccess}
            </a>
          </div>
        </div>
      </div>
    </FadeIn>
  );
}
