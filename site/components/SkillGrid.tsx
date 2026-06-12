"use client";

import { motion } from "framer-motion";
import type { SkillGroup } from "@/lib/skills";

type Props = {
  groups: SkillGroup[];
  compact?: boolean;
};

export function SkillGrid({ groups, compact = false }: Props) {
  return (
    <div className={`grid gap-4 ${compact ? "sm:grid-cols-2" : "sm:grid-cols-2 lg:grid-cols-3"}`}>
      {groups.map((group, gi) => (
        <motion.div
          key={group.title}
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ delay: gi * 0.05, duration: 0.4 }}
          className="rounded-2xl border border-border bg-surface p-5 shadow-card"
        >
          <h3 className="mb-3 font-mono text-xs font-semibold uppercase tracking-widest text-accent">
            {group.title}
          </h3>
          <div className="flex flex-wrap gap-2">
            {group.skills.map((skill) => (
              <span
                key={skill}
                className="rounded-md bg-surface-subtle px-2.5 py-1 text-xs text-ink-muted"
              >
                {skill}
              </span>
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
