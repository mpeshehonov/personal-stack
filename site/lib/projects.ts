import index from "@/content/projects/index.json";

export type Project = {
  slug: string;
  title: string;
  company: string;
  role: string;
  period: string;
  tagline: string;
  problem: string;
  contribution: string;
  stack: string[];
  outcomes: string[];
  featured: boolean;
  order: number;
};

const allProjects = index as Project[];

export function getProjects(): Project[] {
  return [...allProjects].sort((a, b) => a.order - b.order);
}

export function getFeaturedProjects(): Project[] {
  return getProjects().filter((p) => p.featured);
}

export function getProjectBySlug(slug: string): Project | undefined {
  return getProjects().find((p) => p.slug === slug);
}
