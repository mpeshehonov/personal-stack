#!/usr/bin/env node
/**
 * Export site/lib/resume-data.ts → content/resume/*.md for PDF build.
 * Keep in sync with resume-copy skill: no em dashes, no DOB, goal line not ASAP dump.
 */
import { writeFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const runner = path.join(__dirname, ".export-resume-runner.ts");

writeFileSync(
  runner,
  `import { getAboutParagraphs, getExperiences, getAchievements, getEducation } from "../lib/resume-data.ts";
import { getSkillGroups } from "../lib/skills.ts";
const locale = (process.argv[2] === "en" ? "en" : "ru") as "ru" | "en";
console.log(JSON.stringify({
  about: getAboutParagraphs(locale),
  exps: getExperiences(locale),
  edu: getEducation(locale),
  ach: getAchievements(locale),
  skillGroups: getSkillGroups(locale),
}));`
);

function build(locale) {
  const json = execSync(`npx --yes tsx "${runner}" ${locale}`, {
    cwd: root,
    encoding: "utf8",
  });
  return JSON.parse(json);
}

function render(locale, data) {
  const isRu = locale === "ru";
  const header = isRu
    ? `# Максим Пешехонов

Senior Product Engineer | Senior Frontend Engineer

Удалённо, РФ · Email: kassady71@gmail.com · Телефон: +79509196786 · Сайт: [mpeshekhonov.ru](https://mpeshekhonov.ru/ru) · [Telegram: \`@makusimu_san\`](https://t.me/makusimu_san) · [LinkedIn: \`makusimu\`](https://www.linkedin.com/in/makusimu) · [GitHub: \`mpeshehonov\`](https://github.com/mpeshehonov)

**Цель:** remote Senior Product / Frontend Engineer (React, TypeScript) в продуктовой команде.`
    : `# Maksim Peshekhonov

Senior Product Engineer | Senior Frontend Engineer

Remote, Russia · Email: kassady71@gmail.com · Phone: +79509196786 · Site: [mpeshekhonov.ru](https://mpeshekhonov.ru/en) · [Telegram: \`@makusimu_san\`](https://t.me/makusimu_san) · [LinkedIn: \`makusimu\`](https://www.linkedin.com/in/makusimu) · [GitHub: \`mpeshehonov\`](https://github.com/mpeshehonov)

**Goal:** remote Senior Product / Frontend Engineer (React, TypeScript) on a product team.`;

  let md = `${header}\n\n## ${isRu ? "О себе" : "About"}\n\n${data.about.join("\n\n")}\n\n## ${isRu ? "Опыт работы" : "Work experience"}\n\n`;

  for (const exp of data.exps) {
    const link = exp.companyUrl
      ? ` · [${exp.companyUrl.replace(/^https?:\/\//, "").replace(/\/$/, "")}](${exp.companyUrl})`
      : "";
    const blurb = exp.companyBlurb ? `*${exp.companyBlurb}*${link}\n` : "";
    md += `### ${exp.company} - ${exp.role}\n\n${blurb}${exp.period} | ${exp.location}\n\n`;
    for (const b of exp.blocks) {
      md += `**${b.title}** - ${b.tagline}\n\n`;
      for (const o of b.outcomes || []) md += `- ${o}\n`;
      md += `\n${isRu ? "Стек" : "Stack"}: ${b.stack.join(", ")}\n\n`;
    }
  }

  md += renderSkillSection(locale, data.skillGroups);

  md += isRu
    ? `## Языки

- Английский - B1
- Русский - родной

## Образование и сообщество

`
    : `## Languages

- English - B1
- Russian - native

## Education & community

`;

  for (const e of data.edu) {
    md += `${e.school} - ${e.field} (${e.period})\n`;
  }
  md += `\n${data.ach}\n`;
  return md;
}

function renderSkillSection(locale, groups) {
  const heading = locale === "ru" ? "Навыки" : "Skills";
  let md = `## ${heading}\n\n`;
  for (const g of groups) {
    md += `- **${g.title}:** ${g.skills.join(", ")}\n`;
  }
  md += "\n";
  return md;
}

for (const [locale, out] of [
  ["ru", "content/resume/resume.md"],
  ["en", "content/resume/en/resume.md"],
]) {
  writeFileSync(path.join(root, out), render(locale, build(locale)));
  console.log("Wrote", out);
}
