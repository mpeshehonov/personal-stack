#!/usr/bin/env node
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
  const json = execSync(`npx --yes tsx "${runner}" ${locale}`, { cwd: root, encoding: "utf8" });
  return JSON.parse(json);
}

function render(locale, data) {
  const isRu = locale === "ru";
  const header = isRu
    ? `# Максим Пешехонов

Senior Frontend-разработчик

Удалённо, РФ · Email: kassady71@gmail.com · Телефон: +79509196786 · Сайт: [mpeshekhonov.ru](https://mpeshekhonov.ru/ru) · [Telegram: \`@makusimu_san\`](https://t.me/makusimu_san) · [LinkedIn: \`makusimu\`](https://www.linkedin.com/in/makusimu) · [GitHub: \`mpeshehonov\`](https://github.com/mpeshehonov) · Дата рождения: 28.05.1996

**Готов к выходу ASAP.**`
    : `# Maksim Peshekhonov

Senior Frontend Engineer

Remote, Russia · Email: kassady71@gmail.com · Phone: +79509196786 · Site: [mpeshekhonov.ru](https://mpeshekhonov.ru/en) · [Telegram: \`@makusimu_san\`](https://t.me/makusimu_san) · [LinkedIn: \`makusimu\`](https://www.linkedin.com/in/makusimu) · [GitHub: \`mpeshehonov\`](https://github.com/mpeshehonov) · Date of birth: 28.05.1996

**Available to start ASAP.**`;

  let md = `${header}\n\n## ${isRu ? "О себе" : "About"}\n\n${data.about.join("\n\n")}\n\n## ${isRu ? "Опыт работы" : "Work experience"}\n\n`;

  for (const exp of data.exps) {
    md += `### ${exp.company} — ${exp.role}\n\n${exp.period} | ${exp.location}\n\n`;
    for (const b of exp.blocks) {
      md += `**${b.title}**: ${b.tagline}\n\n`;
      md += `${isRu ? "Роль" : "Role"}: ${b.contribution}\n\n`;
      md += `${isRu ? "Результат" : "Outcome"}:\n\n`;
      for (const o of b.outcomes) md += `- ${o}\n`;
      md += `\n${isRu ? "Стек" : "Stack"}: ${b.stack.join(", ")}\n\n`;
    }
  }

  md += renderSkillSection(locale, data.skillGroups);

  md += isRu
    ? `## Иностранные языки

- Английский — B1

## Образование и сообщество

`
    : `## Languages

- English — B1
- Russian — native

## Education & community

`;

  for (const e of data.edu) md += `### ${e.school}\n\n${e.field} · ${e.period} | ${e.location}\n\n`;
  md += data.ach + "\n";
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
