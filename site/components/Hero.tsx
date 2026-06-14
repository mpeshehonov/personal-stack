"use client";

import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import { highlightSkills } from "@/lib/skills";
import { AvailabilityBadge } from "./AvailabilityBadge";
import { FadeIn } from "./FadeIn";
import { parseAvailability } from "@/lib/availability";
import { SocialLinks } from "./SocialLinks";

type ResumeMeta = {
  name: string;
  title: string;
  location: string;
  summary: string;
  availability?: string;
};

type Props = {
  locale: Locale;
  dict: Dictionary;
  resume: ResumeMeta;
};

export function Hero({ locale, dict, resume }: Props) {
  return (
    <FadeIn className="pb-16 pt-10 sm:pb-20 sm:pt-14">
      <div className="card relative overflow-hidden border-0 bg-gradient-to-br from-surface via-surface to-accent-soft p-8 sm:p-10">
        <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-accent/10 blur-3xl" aria-hidden />
        <p className="section-label">{dict.hero.eyebrow}</p>
        <h1 className="mb-2 max-w-3xl text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          {resume.name}
        </h1>
        <p className="mb-2 text-xl text-ink-muted sm:text-2xl">{resume.title}</p>
        <p className="mb-6 flex flex-wrap items-center gap-3 text-sm text-ink-faint">
          <AvailabilityBadge
            status={parseAvailability(resume.availability)}
            dict={dict}
            size="sm"
          />
          <span>{resume.location}</span>
        </p>
        <p className="mb-8 max-w-2xl text-base leading-relaxed text-ink-muted sm:text-lg">
          {resume.summary}
        </p>
        <div className="mb-8 flex flex-wrap gap-3">
          <Link href={localizedPath(locale, "/resume")} className="btn-primary">
            {dict.hero.ctaResume}
            <span aria-hidden>→</span>
          </Link>
          <a href={localizedPath(locale, "/resume/download")} className="btn-secondary">
            {dict.hero.ctaPdf}
          </a>
        </div>
        <SocialLinks className="mb-8" />
        <div>
          <p className="section-label">{dict.hero.skillsLabel}</p>
          <div className="flex flex-wrap gap-2">
            {highlightSkills.map((skill) => (
              <span
                key={skill}
                className="rounded-full border border-border bg-surface px-3 py-1.5 text-sm text-ink-muted"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </FadeIn>
  );
}
