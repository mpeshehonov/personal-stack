import type { Locale } from "@/middleware";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import Link from "next/link";
import resumeRu from "@/content/resume/resume.json";
import resumeEn from "@/content/resume/en/resume.json";
import { Hero } from "@/components/Hero";
import { SkillGrid } from "@/components/SkillGrid";
import { SelectedWork } from "@/components/SelectedWork";
import { BlogPreview } from "@/components/BlogPreview";
import { ProductTeaser } from "@/components/ProductTeaser";
import { ExperiencePreview } from "@/components/ExperiencePreview";
import { FadeIn } from "@/components/FadeIn";
import { getDictionary } from "@/lib/i18n";
import { getHomePreviewExperiences } from "@/lib/experience-preview";
import { getFeaturedProjects } from "@/lib/projects";
import { getLatestBlogPosts } from "@/lib/blog";
import { getSkillGroups } from "@/lib/skills";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const resume = locale === "en" ? resumeEn : resumeRu;
  const featuredProjects = getFeaturedProjects(locale);
  const previewExperiences = getHomePreviewExperiences(locale);
  const latestPosts = getLatestBlogPosts(2);

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
      <BlogPreview locale={locale} dict={dict} posts={latestPosts} />
      <ProductTeaser locale={locale} dict={dict} />
      <FadeIn className="section">
        <p className="section-label">{dict.sections.skills}</p>
        <h2 className="section-title mb-3">{dict.sections.skills}</h2>
        <p className="mb-8 max-w-2xl text-ink-muted">{dict.sections.skillsDesc}</p>
        <SkillGrid groups={getSkillGroups(locale)} />
      </FadeIn>
      <div className="pb-8 text-center">
        <Link href={localizedPath(locale, "/projects")} className="btn-secondary">
          {dict.sections.allProjects}
        </Link>
      </div>
    </>
  );
}
