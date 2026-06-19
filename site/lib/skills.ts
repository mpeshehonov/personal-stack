export type SkillGroup = {
  title: string;
  titleEn?: string;
  skills: string[];
};

export const skillGroupsRu: SkillGroup[] = [
  {
    title: "Языки",
    skills: [
      "TypeScript",
      "JavaScript (ES6+)",
      "HTML5",
      "CSS3",
      "SCSS/SASS",
      "PHP",
      "Python (Django REST)",
      "Node.js",
    ],
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
      "react-router",
      "Tailwind CSS",
      "jQuery",
      "адаптивная вёрстка",
    ],
  },
  {
    title: "1C-Bitrix / CMS",
    skills: [
      "1C-Bitrix",
      "Bitrix (Управление сайтом)",
      "компоненты и шаблоны Bitrix",
      "интернет-магазины",
      "Symfony",
      "MySQL",
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
      "npm-пакеты",
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
    skills: ["Jest", "Vitest", "Playwright", "Sentry", "code review", "Scrum", "Agile"],
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
    skills: [
      "TypeScript",
      "JavaScript (ES6+)",
      "HTML5",
      "CSS3",
      "SCSS/SASS",
      "PHP",
      "Python (Django REST)",
      "Node.js",
    ],
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
      "react-router",
      "Tailwind CSS",
      "jQuery",
      "responsive layout",
    ],
  },
  {
    title: "1C-Bitrix / CMS",
    skills: [
      "1C-Bitrix",
      "Bitrix Site Manager",
      "Bitrix components & templates",
      "online stores",
      "Symfony",
      "MySQL",
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
      "npm packages",
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
    skills: ["Jest", "Vitest", "Playwright", "Sentry", "code review", "Scrum", "Agile"],
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
  "Keycloak",
  "CI/CD",
  "Sentry",
  "e-commerce",
];
