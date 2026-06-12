"use client";

import Link from "next/link";
import type { Dictionary } from "@/lib/i18n";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";
import type { Project } from "@/lib/projects";
import { ProjectCard } from "./ProjectCard";

type Props = {
  locale: Locale;
  dict: Dictionary;
  projects: Project[];
};

export function SelectedWork({ locale, dict, projects }: Props) {
  return (
    <section className="pb-16">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="section-label">{dict.sections.selectedWork}</p>
          <h2 className="section-title">{dict.sections.selectedWork}</h2>
          <p className="mt-2 max-w-xl text-ink-muted">{dict.sections.selectedWorkDesc}</p>
        </div>
        <Link
          href={localizedPath(locale, "/projects")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {dict.sections.allProjects} →
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {projects.map((project) => (
          <ProjectCard key={project.slug} project={project} compact locale={locale} />
        ))}
      </div>
    </section>
  );
}
