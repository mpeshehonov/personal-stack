import type { Experience } from "@/lib/resume-data";
import { getExperiences } from "@/lib/resume-data";

/** Homepage shows the same five employers as /resume (POTALONU through Citilink). */
export function getHomePreviewExperiences(locale: "ru" | "en"): Experience[] {
  return getExperiences(locale);
}
