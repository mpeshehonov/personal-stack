import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import { ExperienceCard } from "./ExperienceCard";
import { FadeIn } from "./FadeIn";
import type { Experience } from "@/lib/resume-data";

type Props = {
  locale: Locale;
  dict: Dictionary;
  experiences: Experience[];
};

export function ExperiencePreview({ locale, dict, experiences }: Props) {
  const desc =
    locale === "en"
      ? "7+ years commercial dev: React/TypeScript e-commerce, 1C-Bitrix stores, enterprise modules. Git, REST, code review."
      : "7+ лет коммерческой разработки: React/TypeScript, e-commerce, 1C-Bitrix, enterprise-модули. Git, REST, code review.";

  return (
    <FadeIn className="section">
      <div className="section-intro">
        <div>
          <p className="section-label">{dict.sections.experience}</p>
          <h2 className="section-title">{dict.sections.experience}</h2>
          <p className="section-desc">{desc}</p>
        </div>
        <Link
          href={localizedPath(locale, "/resume")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {dict.nav.resume} →
        </Link>
      </div>
      <div className="space-y-4">
        {experiences.map((exp, index) => (
          <FadeIn key={exp.company + exp.period} delay={index * 0.08}>
            <ExperienceCard exp={exp} compact locale={locale} />
          </FadeIn>
        ))}
      </div>
    </FadeIn>
  );
}
