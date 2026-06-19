import type { Metadata } from "next";
import Link from "next/link";
import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import { ExperienceCard } from "@/components/ExperienceCard";
import { ResumeHeaderActions } from "@/components/ResumeHeaderActions";
import { SkillGrid } from "@/components/SkillGrid";
import { SocialLinks } from "@/components/SocialLinks";
import { getDictionary, localizedPath } from "@/lib/i18n";
import {
  getAboutParagraphs,
  getAchievements,
  getEducation,
  getExperiences,
} from "@/lib/resume-data";
import { getSkillGroups } from "@/lib/skills";
import { buildPageMetadata } from "@/lib/metadata";
import type { Locale } from "@/middleware";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const resume = locale === "en" ? resumeEn : resumeRu;

  return buildPageMetadata({
    title: dict.nav.resume,
    description: resume.summary,
    locale,
    path: "/resume",
    ogTitle: resume.name,
    ogSubtitle: resume.title,
  });
}

export default async function ResumePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const resume = locale === "en" ? resumeEn : resumeRu;
  const aboutParagraphs = getAboutParagraphs(locale);
  const experiences = getExperiences(locale);
  const educationList = getEducation(locale);
  const achievements = getAchievements(locale);
  const skillGroups = getSkillGroups(locale);
  const langLabel = locale === "en" ? "English — B1" : "Английский — B1";
  const communityLabel = locale === "en" ? "Community" : "Сообщество";
  const languagesLabel = locale === "en" ? "Languages" : "Языки";

  return (
    <article className="resume-print pb-20 pt-8">
      <header className="card mb-10 p-6 sm:p-8">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="mb-1 text-3xl font-bold text-ink sm:text-4xl">{resume.name}</h1>
            <p className="text-lg font-medium text-accent">{resume.title}</p>
            <p className="mt-2 text-ink-faint">{resume.location}</p>
          </div>
          <ResumeHeaderActions locale={locale} dict={dict} />
        </div>
        <div className="mb-6 flex flex-wrap gap-x-4 gap-y-1 text-sm text-ink-muted">
          <a href={`mailto:${resume.email}`} className="hover:text-accent">
            {resume.email}
          </a>
          <span className="text-ink-faint">{resume.phone}</span>
        </div>
        <SocialLinks locale={locale} />
      </header>

      <section className="mb-12">
        <p className="section-label">{dict.resume.about}</p>
        <h2 className="section-title mb-4">{dict.resume.about}</h2>
        <div className="space-y-4 leading-relaxed text-ink-muted">
          {aboutParagraphs.map((p) => (
            <p key={p.slice(0, 40)}>{p}</p>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <p className="section-label">{dict.resume.experience}</p>
        <h2 className="section-title mb-6">{dict.resume.experience}</h2>
        <div className="space-y-4">
          {experiences.map((exp) => (
            <ExperienceCard key={exp.company + exp.period} exp={exp} locale={locale} />
          ))}
        </div>
      </section>

      <section className="mb-12">
        <p className="section-label">{dict.sections.skills}</p>
        <h2 className="section-title mb-6">{dict.sections.skills}</h2>
        <SkillGrid groups={skillGroups} compact />
      </section>

      <section className="mb-12 grid gap-6 sm:grid-cols-2">
        <div className="card">
          <p className="section-label">{languagesLabel}</p>
          <p className="text-ink-muted">{langLabel}</p>
        </div>
        <div className="card">
          <p className="section-label">{dict.resume.education}</p>
          <ul className="mt-4 space-y-4">
            {educationList.map((edu) => (
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

      <section className="card">
        <p className="section-label">{communityLabel}</p>
        <p className="text-sm leading-relaxed text-ink-muted">{achievements}</p>
      </section>

      <p className="mt-8 text-center print:hidden">
        <Link
          href={localizedPath(locale, "/projects")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {locale === "en" ? "All projects" : "Все проекты"} →
        </Link>
      </p>

      <p className="mt-4 text-center print:hidden">
        <Link
          href={localizedPath(locale, "/")}
          className="text-sm text-ink-faint hover:text-accent"
        >
          ← {dict.nav.home}
        </Link>
      </p>
    </article>
  );
}
