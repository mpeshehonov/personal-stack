import type { Metadata } from "next";
import { ProjectCard } from "@/components/ProjectCard";
import { getProjects } from "@/lib/projects";

export const metadata: Metadata = {
  title: "Проекты",
  description:
    "Кейсы: X5 Tech, НЛМК, Telegram Mini Apps, e-commerce миграции и self-hosted fullstack.",
  openGraph: {
    title: "Проекты — Максим Пешехонов",
    description:
      "Кейсы: X5 Tech, НЛМК, Telegram Mini Apps, e-commerce миграции и self-hosted fullstack.",
    url: "https://mpeshekhonov.ru/projects",
  },
};

export default function ProjectsPage() {
  const projects = getProjects();

  return (
    <article className="pb-20 pt-8">
      <header className="mb-10">
        <h1 className="mb-2 text-3xl font-bold text-ink sm:text-4xl">
          Проекты
        </h1>
        <p className="max-w-2xl text-ink-muted">
          Кейсы из реального опыта: задача → роль → стек → результат. Каждый
          проект — с метриками или измеримым impact.
        </p>
      </header>

      <div className="space-y-6">
        {projects.map((project) => (
          <ProjectCard key={project.slug} project={project} />
        ))}
      </div>
    </article>
  );
}
