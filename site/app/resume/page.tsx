import type { Metadata } from "next";
import Link from "next/link";
import resume from "@/content/resume/resume.json";
import { ExperienceCard } from "@/components/ExperienceCard";
import { SkillGrid } from "@/components/SkillGrid";
import { SocialLinks } from "@/components/SocialLinks";
import {
  aboutText,
  achievements,
  education,
  experiences,
} from "@/lib/resume-data";
import { skillGroups } from "@/lib/skills";

const resumeUrl = "https://mpeshekhonov.ru/resume";
const resumeTitle = `Резюме — ${resume.name}`;

export const metadata: Metadata = {
  title: resumeTitle,
  description: aboutText,
  openGraph: {
    title: resumeTitle,
    description: aboutText,
    url: resumeUrl,
    siteName: resume.name,
    locale: "ru_RU",
    type: "profile",
  },
};

export default function ResumePage() {
  return (
    <article className="pb-20 pt-8">
      <header className="mb-10 rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md sm:p-8">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="mb-1 text-3xl font-bold text-ink sm:text-4xl">
              {resume.name}
            </h1>
            <p className="text-lg text-accent">{resume.title}</p>
            <p className="mt-2 text-ink-faint">{resume.location}</p>
          </div>
          <a
            href="/resume/download"
            className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-surface shadow-lg shadow-accent/20 transition hover:bg-accent-dim"
          >
            Скачать PDF
          </a>
        </div>

        <div className="mb-6 flex flex-wrap gap-x-4 gap-y-1 text-sm text-ink-muted">
          <a href={`mailto:${resume.email}`} className="hover:text-accent">
            {resume.email}
          </a>
          <span className="text-ink-faint">{resume.phone}</span>
        </div>

        <SocialLinks />
      </header>

      <section className="mb-12">
        <h2 className="mb-4 font-mono text-xs uppercase tracking-widest text-accent">
          О себе
        </h2>
        <p className="leading-relaxed text-ink-muted">{aboutText}</p>
      </section>

      <section className="mb-12">
        <h2 className="mb-6 font-mono text-xs uppercase tracking-widest text-accent">
          Опыт работы
        </h2>
        <div className="space-y-4">
          {experiences.map((exp) => (
            <ExperienceCard key={exp.company + exp.period} exp={exp} />
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="mb-6 font-mono text-xs uppercase tracking-widest text-accent">
          Навыки
        </h2>
        <SkillGrid groups={skillGroups} compact />
      </section>

      <section className="mb-12 grid gap-6 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md">
          <h2 className="mb-4 font-mono text-xs uppercase tracking-widest text-accent">
            Языки
          </h2>
          <p className="text-ink-muted">Английский — B1</p>
        </div>
        <div className="rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md">
          <h2 className="mb-4 font-mono text-xs uppercase tracking-widest text-accent">
            Образование
          </h2>
          <ul className="space-y-4">
            {education.map((edu) => (
              <li key={edu.school}>
                <p className="font-medium text-ink">{edu.school}</p>
                <p className="text-sm text-ink-muted">
                  {edu.field} · {edu.period}
                </p>
                <p className="text-sm text-ink-faint">{edu.location}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-accent">
          Сообщество
        </h2>
        <p className="text-sm leading-relaxed text-ink-muted">{achievements}</p>
      </section>

      <p className="mt-8 text-center">
        <Link href="/" className="text-sm text-ink-faint hover:text-accent">
          ← На главную
        </Link>
      </p>
    </article>
  );
}
