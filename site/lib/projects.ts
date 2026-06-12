import index from "@/content/projects/index.json";
import type { Locale } from "@/middleware";

export type LocaleField = {
  ru: string;
  en: string;
};

export type ProjectRecord = {
  slug: string;
  title: LocaleField;
  company: LocaleField;
  role: LocaleField;
  tagline: LocaleField;
  problem: LocaleField;
  contribution: LocaleField;
  stack: string[];
  outcomes: {
    ru: string[];
    en: string[];
  };
  featured: boolean;
  order: number;
};

export type Project = {
  slug: string;
  title: string;
  company: string;
  role: string;
  tagline: string;
  problem: string;
  contribution: string;
  stack: string[];
  outcomes: string[];
  featured: boolean;
  order: number;
};

const allProjects = index as ProjectRecord[];

function localize(record: ProjectRecord, locale: Locale): Project {
  return {
    slug: record.slug,
    title: record.title[locale],
    company: record.company[locale],
    role: record.role[locale],
    tagline: record.tagline[locale],
    problem: record.problem[locale],
    contribution: record.contribution[locale],
    stack: record.stack,
    outcomes: record.outcomes[locale],
    featured: record.featured,
    order: record.order,
  };
}

export function getProjects(locale: Locale = "ru"): Project[] {
  return [...allProjects].map((p) => localize(p, locale)).sort((a, b) => a.order - b.order);
}

export function getFeaturedProjects(locale: Locale = "ru"): Project[] {
  return getProjects(locale).filter((p) => p.featured);
}

export function getProjectBySlug(slug: string, locale: Locale = "ru"): Project | undefined {
  return getProjects(locale).find((p) => p.slug === slug);
}
