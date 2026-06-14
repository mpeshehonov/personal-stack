"use client";

import type { Project } from "@/lib/projects";
import type { Locale } from "@/middleware";
import { FadeIn } from "./FadeIn";
import { ProjectCard } from "./ProjectCard";

type Props = {
  projects: Project[];
  locale: Locale;
};

export function AnimatedProjectList({ projects, locale }: Props) {
  return (
    <div className="space-y-6">
      {projects.map((project, index) => (
        <FadeIn key={project.slug} delay={index * 0.06}>
          <ProjectCard project={project} locale={locale} />
        </FadeIn>
      ))}
    </div>
  );
}
