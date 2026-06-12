"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ExperienceCard } from "./ExperienceCard";
import type { Experience } from "@/lib/resume-data";

type Props = {
  experiences: Experience[];
};

export function ExperiencePreview({ experiences }: Props) {
  return (
    <section className="pb-20">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="mb-2 font-mono text-xs uppercase tracking-widest text-accent">
            Опыт
          </h2>
          <p className="max-w-xl text-ink-muted">
            7+ лет в продакшене: от e-commerce миграций до enterprise RBAC и
            self-hosted fullstack.
          </p>
        </div>
        <Link href="/resume" className="text-sm text-accent hover:underline">
          Полное резюме →
        </Link>
      </div>

      <div className="space-y-4">
        {experiences.map((exp, i) => (
          <motion.div
            key={exp.company + exp.period}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: i * 0.06, duration: 0.4 }}
          >
            <ExperienceCard exp={exp} />
          </motion.div>
        ))}
      </div>
    </section>
  );
}
