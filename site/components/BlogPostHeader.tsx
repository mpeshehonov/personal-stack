import Link from "next/link";

type Props = {
  href: string;
  label: string;
  date: string;
  title: string;
  tags: string[];
};

export function BlogPostHeader({ href, label, date, title, tags }: Props) {
  return (
    <header className="mb-12 border-b border-border pb-8">
      <nav className="mb-6">
        <Link
          href={href}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-muted transition hover:text-accent"
        >
          <span aria-hidden className="text-base leading-none">
            ←
          </span>
          {label}
        </Link>
      </nav>
      <div className="flex flex-col gap-4 sm:gap-5">
        <time
          dateTime={date}
          className="font-mono text-xs uppercase tracking-wider text-ink-faint"
        >
          {date}
        </time>
        <h1 className="max-w-3xl text-3xl font-bold tracking-tight text-ink sm:text-4xl lg:text-[2.5rem] lg:leading-tight">
          {title}
        </h1>
        {tags.length > 0 && (
          <ul className="flex flex-wrap gap-2" aria-label="Tags">
            {tags.map((tag) => (
              <li key={tag}>
                <span className="rounded-lg bg-accent-soft px-2.5 py-1 text-xs font-medium text-accent">
                  {tag}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </header>
  );
}
