"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import resume from "@/content/resume/resume.json";
import { highlightSkills } from "@/lib/skills";
import { SocialLinks } from "./SocialLinks";

export function Hero() {
  return (
    <section className="relative overflow-hidden pb-16 pt-12 sm:pb-24 sm:pt-20">
      <div className="pointer-events-none absolute -left-32 top-0 h-64 w-64 rounded-full bg-accent/10 blur-3xl" />
      <div className="pointer-events-none absolute -right-20 bottom-0 h-48 w-48 rounded-full bg-indigo-500/10 blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative"
      >
        <p className="mb-3 font-mono text-sm text-accent">// senior frontend dev</p>
        <h1 className="mb-2 text-4xl font-bold tracking-tight text-ink sm:text-5xl lg:text-6xl">
          {resume.name}
        </h1>
        <p className="mb-1 text-xl text-ink-muted sm:text-2xl">{resume.title}</p>
        <p className="mb-8 flex items-center gap-2 text-ink-faint">
          <span className="inline-block h-2 w-2 animate-pulse-glow rounded-full bg-accent" />
          {resume.location}
        </p>

        <p className="mb-8 max-w-2xl text-base leading-relaxed text-ink-muted sm:text-lg">
          {resume.summary}
        </p>

        <div className="mb-10 flex flex-wrap gap-3">
          <Link
            href="/resume"
            className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-surface shadow-lg shadow-accent/20 transition hover:bg-accent-dim"
          >
            Смотреть резюме
            <span aria-hidden>→</span>
          </Link>
          <a
            href="/resume/download"
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-ink backdrop-blur-sm transition hover:border-accent/30 hover:text-accent"
          >
            Скачать PDF
          </a>
        </div>

        <SocialLinks className="mb-10" />

        <div>
          <p className="mb-3 font-mono text-xs uppercase tracking-widest text-ink-faint">
            Ключевые технологии
          </p>
          <div className="flex flex-wrap gap-2">
            {highlightSkills.map((skill, i) => (
              <motion.span
                key={skill}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 + i * 0.04 }}
                className="rounded-full border border-accent/20 bg-accent/8 px-3 py-1.5 text-sm text-accent"
              >
                {skill}
              </motion.span>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}
