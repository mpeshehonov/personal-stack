import ru from "@/content/i18n/ru.json";
import en from "@/content/i18n/en.json";
import type { Locale } from "@/middleware";

export type Dictionary = typeof ru;

const dictionaries: Record<Locale, Dictionary> = { ru, en };

export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale] ?? dictionaries.ru;
}

export function localizedPath(locale: Locale, path: string): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  if (clean === "/") return `/${locale}`;
  return `/${locale}${clean}`;
}

export const pdfByLocale: Record<Locale, { file: string; downloadName: string }> = {
  ru: {
    file: "Maksim_Peshekhonov_CV_RU.pdf",
    downloadName: "Maksim_Peshekhonov_CV_RU.pdf",
  },
  en: {
    file: "Maksim_Peshekhonov_CV_EN.pdf",
    downloadName: "Maksim_Peshekhonov_CV_EN.pdf",
  },
};
