import type { Project } from "@/lib/projects";
import Link from "next/link";
import { localizedPath } from "@/lib/i18n";
import type { Locale } from "@/middleware";

type Props = {
  project: Project;
  compact?: boolean;
  locale?: Locale;
};

export function ProjectCard({ project, compact = false, locale = "ru" }: Props) {
  const labels =
    locale === "en"
      ? { problem: "Problem", role: "Role", result: "Outcome", more: "Details" }
      : { problem: "Задача", role: "Роль", result: "Результат", more: "Подробнее" };

  return (
    <article className="card transition hover:shadow-lift">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="font-mono text-xs font-medium text-accent">{project.company}</p>
          <h3 className="text-lg font-semibold text-ink">{project.title}</h3>
        </div>
        <p className="text-sm text-ink-faint">{project.period}</p>
      </div>
      <p className="mb-4 text-sm text-ink-muted">{project.tagline}</p>
      <div className="mb-4 flex flex-wrap gap-2">
        {project.stack.slice(0, compact ? 5 : 8).map((tech) => (
          <span
            key={tech}
            className="rounded-md bg-surface-subtle px-2.5 py-1 text-xs text-ink-muted"
          >
            {tech}
          </span>
        ))}
      </div>
      {!compact && (
        <div className="space-y-3 text-sm text-ink-muted">
          <div>
            <p className="mb-1 font-mono text-xs uppercase tracking-wider text-ink-faint">
              {labels.problem}
            </p>
            <p>{project.problem}</p>
          </div>
          <div>
            <p className="mb-1 font-mono text-xs uppercase tracking-wider text-ink-faint">
              {labels.role}
            </p>
            <p>{project.contribution}</p>
          </div>
          <ul className="space-y-1">
            {project.outcomes.map((o) => (
              <li key={o} className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                {o}
              </li>
            ))}
          </ul>
        </div>
      )}
      {compact && (
        <Link
          href={localizedPath(locale, "/projects")}
          className="text-sm font-medium text-accent hover:underline"
        >
          {labels.more} →
        </Link>
      )}
    </article>
  );
}
