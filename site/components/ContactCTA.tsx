"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import resume from "@/content/resume/resume.json";
import { SocialLinks } from "./SocialLinks";

export function ContactCTA() {
  return (
    <section className="pb-24">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-40px" }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden rounded-2xl border border-accent/20 bg-accent/5 p-8 backdrop-blur-md sm:p-10"
      >
        <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-accent/10 blur-3xl" />

        <div className="relative">
          <h2 className="mb-2 font-mono text-xs uppercase tracking-widest text-accent">
            Связаться
          </h2>
          <p className="mb-2 text-2xl font-bold text-ink sm:text-3xl">
            Открыт к предложениям
          </p>
          <p className="mb-8 max-w-lg text-ink-muted">
            Senior Frontend / Fullstack — удалённо или гибрид. Напишите в
            Telegram или на почту, отвечу в течение дня.
          </p>

          <div className="mb-8 flex flex-wrap gap-3">
            <a
              href={resume.links.telegram}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-surface shadow-lg shadow-accent/20 transition hover:bg-accent-dim"
            >
              Написать в Telegram
              <span aria-hidden>→</span>
            </a>
            <a
              href={`mailto:${resume.email}`}
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-ink backdrop-blur-sm transition hover:border-accent/30 hover:text-accent"
            >
              {resume.email}
            </a>
          </div>

          <SocialLinks />
        </div>
      </motion.div>
    </section>
  );
}
