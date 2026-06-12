import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import type { Locale } from "@/middleware";
import type { Dictionary } from "@/lib/i18n";
import { SocialLinks } from "./SocialLinks";

type Props = {
  locale: Locale;
  dict: Dictionary;
};

export function ContactCTA({ locale, dict }: Props) {
  const resume = locale === "en" ? resumeEn : resumeRu;
  const desc =
    locale === "en"
      ? "Senior Frontend / Fullstack — remote or hybrid. Message on Telegram or email; I usually reply within a day."
      : "Senior Frontend / Fullstack — удалённо или гибрид. Напишите в Telegram или на почту, отвечу в течение дня.";

  return (
    <section className="pb-16">
      <div className="card bg-gradient-to-br from-accent-soft to-surface p-8 sm:p-10">
        <p className="section-label">{dict.sections.contact}</p>
        <h2 className="section-title mb-3">{dict.cta.openToOffers}</h2>
        <p className="mb-8 max-w-lg text-ink-muted">{desc}</p>
        <div className="mb-8 flex flex-wrap gap-3">
          <a href={resume.links.telegram} target="_blank" rel="noopener noreferrer" className="btn-primary">
            {dict.cta.telegram}
            <span aria-hidden>→</span>
          </a>
          <a href={`mailto:${resume.email}`} className="btn-secondary">
            {dict.cta.email}
          </a>
        </div>
        <SocialLinks />
      </div>
    </section>
  );
}
