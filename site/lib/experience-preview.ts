import type { Experience } from "@/lib/resume-data";
import { getExperiences } from "@/lib/resume-data";

/** Companies shown on the homepage experience block (Citilink included). */
const HOME_PREVIEW_COMPANIES = [
  "POTALONU LLC",
  "X5 Tech",
  "Citilink",
  "НЛМК",
  "NLMK",
] as const;

export function getHomePreviewExperiences(locale: "ru" | "en"): Experience[] {
  const all = getExperiences(locale);
  const picked: Experience[] = [];
  for (const name of HOME_PREVIEW_COMPANIES) {
    const exp = all.find((e) => e.company === name);
    if (exp && !picked.some((p) => p.company === exp.company)) {
      picked.push(exp);
    }
  }
  return picked.slice(0, 4);
}
