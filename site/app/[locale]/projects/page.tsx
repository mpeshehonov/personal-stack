import { AnimatedProjectList } from "@/components/AnimatedProjectList";
import { getDictionary } from "@/lib/i18n";
import { getProjects } from "@/lib/projects";
import type { Locale } from "@/middleware";

export default async function ProjectsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: raw } = await params;
  const locale = (raw === "en" ? "en" : "ru") as Locale;
  const dict = getDictionary(locale);
  const projects = getProjects(locale);
  const desc =
    locale === "en"
      ? "Real case studies: problem → role → stack → outcome."
      : "Кейсы из реального опыта: задача → роль → стек → результат.";

  return (
    <article className="pb-20 pt-8">
      <header className="mb-10">
        <p className="section-label">{dict.nav.projects}</p>
        <h1 className="section-title mb-3">{dict.nav.projects}</h1>
        <p className="max-w-2xl text-ink-muted">{desc}</p>
      </header>
      <AnimatedProjectList projects={projects} locale={locale} />
    </article>
  );
}
