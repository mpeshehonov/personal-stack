import type { Experience } from "@/lib/resume-data";
import type { Locale } from "@/middleware";

type Props = {
  exp: Experience;
  compact?: boolean;
  locale?: Locale;
};

export function ExperienceCard({ exp, compact = false, locale = "ru" }: Props) {
  const labels =
    locale === "en"
      ? { problem: "Problem", role: "Role", result: "Outcome" }
      : { problem: "Задача", role: "Роль", result: "Результат" };

  return (
    <article className="card transition hover:shadow-lift">
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h3 className="text-lg font-semibold text-ink">{exp.company}</h3>
          <p className="text-sm font-medium text-accent">{exp.role}</p>
        </div>
        <div className="text-right text-sm text-ink-faint">
          <p>{exp.period}</p>
          <p>{exp.location}</p>
        </div>
      </div>
      <div className="space-y-6">
        {exp.blocks.map((block) => (
          <div key={block.title} className="border-t border-surface-subtle pt-5 first:border-0 first:pt-0">
            <p className="font-mono text-xs font-medium text-accent">{block.title}</p>
            <p className="mt-1 text-sm text-ink-muted">{block.tagline}</p>
            <div className="my-3 flex flex-wrap gap-2">
              {block.stack.slice(0, compact ? 5 : 8).map((tech) => (
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
                  <p>{block.problem}</p>
                </div>
                <div>
                  <p className="mb-1 font-mono text-xs uppercase tracking-wider text-ink-faint">
                    {labels.role}
                  </p>
                  <p>{block.contribution}</p>
                </div>
                <ul className="space-y-1">
                  {block.outcomes.map((o) => (
                    <li key={o} className="flex gap-2">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                      {o}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {compact && (
              <ul className="mt-2 space-y-1 text-sm text-ink-muted">
                {block.outcomes.slice(0, 2).map((o) => (
                  <li key={o} className="flex gap-2">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                    {o}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </article>
  );
}
