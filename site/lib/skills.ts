export type SkillGroup = {
  title: string;
  titleEn?: string;
  skills: string[];
};

export const skillGroupsRu: SkillGroup[] = [
  {
    title: "Языки",
    skills: ["TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3", "SCSS/SASS", "Python", "Node.js"],
  },
  {
    title: "Frontend",
    skills: [
      "React",
      "Next.js (SSR/SSG)",
      "Redux Toolkit",
      "MobX",
      "TanStack Query",
      "TanStack Table",
      "React Hook Form",
      "Zod",
      "Feature-Sliced Design",
      "Module Federation",
      "Tailwind CSS",
      "CSS-in-JS / Emotion",
    ],
  },
  {
    title: "Сборка и Git",
    skills: [
      "Git",
      "Webpack",
      "Vite",
      "yarn workspaces",
      "монорепозитории",
      "code splitting",
      "GitLab CI",
      "GitHub Actions",
      "Docker",
      "CI/CD",
    ],
  },
  {
    title: "API и backend",
    skills: [
      "REST API",
      "OpenAPI/Orval",
      "GraphQL (Apollo Client)",
      "WebSocket",
      "PostgreSQL",
      "SQL",
      "Drizzle ORM",
      "Nest.js",
      "Django REST",
      "Keycloak",
      "Auth.js",
    ],
  },
  {
    title: "Качество и процессы",
    skills: ["Jest", "Vitest", "React Testing Library", "Playwright", "Storybook", "Sentry", "code review", "Scrum", "Agile"],
  },
  {
    title: "UI & продукт",
    skills: [
      "e-commerce",
      "дизайн-системы",
      "UI Kit",
      "Material UI",
      "Figma",
      "Telegram Mini Apps",
      "i18next",
      "next-intl",
    ],
  },
];

export const skillGroupsEn: SkillGroup[] = [
  {
    title: "Languages",
    skills: ["TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3", "SCSS/SASS", "Python", "Node.js"],
  },
  {
    title: "Frontend",
    skills: [
      "React",
      "Next.js (SSR/SSG)",
      "Redux Toolkit",
      "MobX",
      "TanStack Query",
      "TanStack Table",
      "React Hook Form",
      "Zod",
      "Feature-Sliced Design",
      "Module Federation",
      "Tailwind CSS",
      "CSS-in-JS / Emotion",
    ],
  },
  {
    title: "Build & Git",
    skills: [
      "Git",
      "Webpack",
      "Vite",
      "yarn workspaces",
      "monorepos",
      "code splitting",
      "GitLab CI",
      "GitHub Actions",
      "Docker",
      "CI/CD",
    ],
  },
  {
    title: "API & backend",
    skills: [
      "REST API",
      "OpenAPI/Orval",
      "GraphQL (Apollo Client)",
      "WebSocket",
      "PostgreSQL",
      "SQL",
      "Drizzle ORM",
      "Nest.js",
      "Django REST",
      "Keycloak",
      "Auth.js",
    ],
  },
  {
    title: "Quality & process",
    skills: ["Jest", "Vitest", "React Testing Library", "Playwright", "Storybook", "Sentry", "code review", "Scrum", "Agile"],
  },
  {
    title: "UI & product",
    skills: [
      "e-commerce",
      "design systems",
      "UI Kit",
      "Material UI",
      "Figma",
      "Telegram Mini Apps",
      "i18next",
      "next-intl",
    ],
  },
];

export function getSkillGroups(locale: "ru" | "en"): SkillGroup[] {
  return locale === "en" ? skillGroupsEn : skillGroupsRu;
}

/** @deprecated use getSkillGroups */
export const skillGroups = skillGroupsRu;

export const highlightSkills = [
  "React",
  "TypeScript",
  "Next.js",
  "Vite",
  "OpenAPI/Orval",
  "TanStack Query",
  "React Hook Form",
  "GraphQL",
  "WebSocket",
  "Keycloak",
  "FSD",
  "Module Federation",
  "Material UI",
  "CI/CD",
  "Sentry",
  "e-commerce",
];
