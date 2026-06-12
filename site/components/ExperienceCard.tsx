import type { Experience } from "@/lib/resume-data";

export function ExperienceCard({ exp }: { exp: Experience }) {
  return (
    <article className="card">
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
      {exp.projects?.map((project) => (
        <div key={project.name} className="mb-4 last:mb-0">
          <p className="mb-1 font-medium text-ink">{project.name}</p>
          <p className="mb-2 font-mono text-xs text-ink-faint">{project.stack}</p>
          <ul className="space-y-1.5 text-sm text-ink-muted">
            {project.bullets.map((b) => (
              <li key={b} className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                {b}
              </li>
            ))}
          </ul>
        </div>
      ))}
      {exp.bullets && (
        <ul className="space-y-1.5 text-sm text-ink-muted">
          {exp.bullets.map((b) => (
            <li key={b} className="flex gap-2">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
              {b}
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
