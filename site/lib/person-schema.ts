import type { Locale } from "@/middleware";

type ResumeForSchema = {
  name: string;
  title: string;
  email: string;
  location: string;
  summary: string;
  skills: string[];
  links: {
    telegram?: string;
    linkedin?: string;
    github?: string;
  };
};

export function buildPersonJsonLd(locale: Locale, resume: ResumeForSchema) {
  const baseUrl = "https://mpeshekhonov.ru";
  const sameAs = [resume.links.linkedin, resume.links.github, resume.links.telegram].filter(
    Boolean,
  ) as string[];

  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name: resume.name,
    jobTitle: resume.title,
    email: resume.email,
    url: `${baseUrl}/${locale}`,
    description: resume.summary,
    knowsAbout: resume.skills,
    sameAs,
    address: {
      "@type": "PostalAddress",
      addressLocality: resume.location,
    },
  };
}
