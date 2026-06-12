import type { Project } from "@/lib/projects";
import Link from "next/link";

type Props = {
  project: Project;
  compact?: boolean;
};

export function ProjectCard({ project, compact = false }: Props) {
  return (
    <article className="group rounded-2xl border border-white/8 bg-surface-glass p-6 backdrop-blur-md transition hover:border-accent/20">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="font-mono text-xs text-accent">{project.company}</p>
          <h3 className="text-lg font-semibold text-ink group-hover:text-accent transition-colors">
            {project.title}
          </h3>
        </div>
        <p className="text-sm text-ink-faint">{project.period}</p>
      </div>

      <p className="mb-4 text-sm text-ink-muted">{project.tagline}</p>

      <div className="mb-4 flex flex-wrap gap-2">
        {project.stack.slice(0, compact ? 4 : 6).map((tech) => (
          <span
            key={tech}
            className="rounded-lg border border-white/6 bg-white/4 px-2.5 py-1 text-xs text-ink-muted"
          >
            {tech}
          </span>
        ))}
        {compact && project.stack.length > 4 && (
          <span className="rounded-lg px-2.5 py-1 text-xs text-ink-faint">
            +{project.stack.length - 4}
          </span>
        )}
      </div>

      {!compact && (
        <div className="mb-4 space-y-3 text-sm text-ink-muted">
          <div>
            <p className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-faint">
              Задача
            </p>
            <p>{project.problem}</p>
          </div>
          <div>
            <p className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-faint">
              Роль
            </p>
            <p>{project.contribution}</p>
          </div>
          <div>
            <p className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-faint">
              Результат
            </p>
            <ul className="space-y-1">
              {project.outcomes.map((o) => (
                <li key={o} className="flex gap-2">
                  <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-accent/60" />
                  {o}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {compact && (
        <Link
          href="/projects"
          className="inline-flex items-center gap-1 text-sm text-accent hover:underline"
        >
          Подробнее
          <span aria-hidden>→</span>
        </Link>
      )}
    </article>
  );
}
