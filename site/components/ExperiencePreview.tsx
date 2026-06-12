import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import { ExperienceCard } from "./ExperienceCard";
import type { Experience } from "@/lib/resume-data";

type Props = {
  locale: Locale;
  dict: Dictionary;
  experiences: Experience[];
};

export function ExperiencePreview({ locale, dict, experiences }: Props) {
  const desc =
    locale === "en"
      ? "7+ years in production — from e-commerce migrations to enterprise RBAC and self-hosted fullstack."
      : "7+ лет в продакшене: от e-commerce миграций до enterprise RBAC и self-hosted fullstack.";

  return (
    <section className="pb-16">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="section-label">{dict.sections.experience}</p>
          <h2 className="section-title">{dict.sections.experience}</h2>
          <p className="mt-2 max-w-xl text-ink-muted">{desc}</p>
        </div>
        <Link
          href={localizedPath(locale, "/resume")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {dict.nav.resume} →
        </Link>
      </div>
      <div className="space-y-4">
        {experiences.map((exp) => (
          <ExperienceCard key={exp.company + exp.period} exp={exp} />
        ))}
      </div>
    </section>
  );
}
