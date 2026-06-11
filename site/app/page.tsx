import { Hero } from "@/components/Hero";
import { SkillGrid } from "@/components/SkillGrid";
import { skillGroups } from "@/lib/skills";

export default function HomePage() {
  return (
    <>
      <Hero />
      <section className="pb-20">
        <h2 className="mb-2 font-mono text-xs uppercase tracking-widest text-accent">
          Навыки
        </h2>
        <p className="mb-8 max-w-xl text-ink-muted">
          Полный стек — от сложных UI и визуализаций до fullstack, DevOps и
          наблюдаемости в продакшене.
        </p>
        <SkillGrid groups={skillGroups} />
      </section>
    </>
  );
}
