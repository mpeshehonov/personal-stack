import type { Locale } from "@/middleware";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import Link from "next/link";
import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import { Hero } from "@/components/Hero";
import { SkillGrid } from "@/components/SkillGrid";
import { SelectedWork } from "@/components/SelectedWork";
import { ExperiencePreview } from "@/components/ExperiencePreview";
import { ContactCTA } from "@/components/ContactCTA";
import { getDictionary } from "@/lib/i18n";
import { getExperiences } from "@/lib/resume-data";
import { getFeaturedProjects } from "@/lib/projects";
import { skillGroups } from "@/lib/skills";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const resume = locale === "en" ? resumeEn : resumeRu;
  const featuredProjects = getFeaturedProjects();
  const previewExperiences = getExperiences(locale).slice(0, 3);

  return (
    <>
      <Hero locale={locale} dict={dict} resume={resume} />
      <SelectedWork
        locale={locale}
        dict={dict}
        projects={featuredProjects}
      />
      <ExperiencePreview
        locale={locale}
        dict={dict}
        experiences={previewExperiences}
      />
      <section className="pb-16">
        <p className="section-label">{dict.sections.skills}</p>
        <h2 className="section-title mb-3">{dict.sections.skills}</h2>
        <p className="mb-8 max-w-2xl text-ink-muted">{dict.sections.skillsDesc}</p>
        <SkillGrid groups={skillGroups} />
      </section>
      <ContactCTA locale={locale} dict={dict} />
      <div className="pb-8 text-center">
        <Link href={localizedPath(locale, "/projects")} className="btn-secondary">
          {dict.sections.allProjects}
        </Link>
      </div>
    </>
  );
}
