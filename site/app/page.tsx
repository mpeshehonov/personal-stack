import type { Metadata } from "next";
import { Hero } from "@/components/Hero";
import { SkillGrid } from "@/components/SkillGrid";
import { SelectedWork } from "@/components/SelectedWork";
import { ExperiencePreview } from "@/components/ExperiencePreview";
import { ContactCTA } from "@/components/ContactCTA";
import { getFeaturedProjects } from "@/lib/projects";
import { experiences } from "@/lib/resume-data";
import { skillGroups } from "@/lib/skills";

export default function HomePage() {
  const featuredProjects = getFeaturedProjects();
  const previewExperiences = experiences.slice(0, 3);

  return (
    <>
      <Hero />
      <SelectedWork projects={featuredProjects} />
      <ExperiencePreview experiences={previewExperiences} />
      <section className="pb-20">
        <h2 className="mb-2 font-mono text-xs uppercase tracking-widest text-accent">
          Навыки
        </h2>
        <p className="mb-8 max-w-xl text-ink-muted">
          Полный стек — от сложных UI и визуализаций до fullstack, DevOps и
          наблюдаемости в продакшене.
        </p>
        <SkillGrid groups={skillGroups} />
      </section>
      <ContactCTA />
    </>
  );
}
