"use client";

import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import type { Project } from "@/lib/projects";
import { ProjectCard } from "./ProjectCard";
import { FadeIn } from "./FadeIn";

type Props = {
  locale: Locale;
  dict: Dictionary;
  projects: Project[];
};

export function SelectedWork({ locale, dict, projects }: Props) {
  return (
    <FadeIn className="section">
      <div className="section-intro">
        <div>
          <p className="section-label">{dict.sections.selectedWork}</p>
          <h2 className="section-title">{dict.sections.selectedWork}</h2>
          <p className="section-desc">{dict.sections.selectedWorkDesc}</p>
        </div>
        <Link
          href={localizedPath(locale, "/projects")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {dict.sections.allProjects} →
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {projects.map((project, index) => (
          <FadeIn key={project.slug} delay={index * 0.08}>
            <ProjectCard project={project} compact locale={locale} />
          </FadeIn>
        ))}
      </div>
    </FadeIn>
  );
}
