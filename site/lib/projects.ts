import x5 from "@/content/projects/x5-procurement.json";
import nlmk from "@/content/projects/nlmk-iron-registration.json";
import seatMap from "@/content/projects/potalonu-seat-map.json";
import sendonate from "@/content/projects/sendonate-donations.json";
import citilink from "@/content/projects/citilink-migration.json";

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

const allProjects: Project[] = [x5, nlmk, seatMap, sendonate, citilink];

export function getProjects(): Project[] {
  return [...allProjects].sort((a, b) => a.order - b.order);
}

export function getFeaturedProjects(): Project[] {
  return getProjects().filter((p) => p.featured);
}

export function getProjectBySlug(slug: string): Project | undefined {
  return getProjects().find((p) => p.slug === slug);
}
