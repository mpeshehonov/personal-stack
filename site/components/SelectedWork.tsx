"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { Project } from "@/lib/projects";
import { ProjectCard } from "./ProjectCard";

type Props = {
  projects: Project[];
};

export function SelectedWork({ projects }: Props) {
  return (
    <section className="pb-20">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="mb-2 font-mono text-xs uppercase tracking-widest text-accent">
            Избранные проекты
          </h2>
          <p className="max-w-xl text-ink-muted">
            Кейсы с измеримым impact: enterprise, e-commerce, real-time и
            Telegram Mini Apps.
          </p>
        </div>
        <Link
          href="/projects"
          className="text-sm text-accent hover:underline"
        >
          Все проекты →
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {projects.map((project, i) => (
          <motion.div
            key={project.slug}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: i * 0.06, duration: 0.4 }}
          >
            <ProjectCard project={project} compact />
          </motion.div>
        ))}
      </div>
    </section>
  );
}
