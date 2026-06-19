export type SkillGroup = {
  title: string;
  titleEn?: string;
  skills: string[];
};

export const skillGroupsRu: SkillGroup[] = [
  {
    title: "Языки",
    skills: ["TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3/SCSS", "PHP", "Node.js", "Golang"],
  },
  {
    title: "Frontend",
    skills: [
      "React",
      "Next.js (SSR/SSG)",
      "Redux Toolkit",
      "Redux-Saga",
      "MobX",
      "Effector",
      "TanStack Query",
      "TanStack Table",
      "React Hook Form",
      "Zod",
      "Formik",
      "react-router",
      "Framer Motion",
      "Radix UI",
      "Tailwind CSS",
      "FSD",
    ],
  },
  {
    title: "Визуализация",
    skills: [
      "Cytoscape.js",
      "Highcharts",
      "Recharts",
      "react-grid-layout",
      "react-virtualized",
      "@tanstack/react-virtual",
      "Canvas",
      "Leaflet",
      "Yandex Maps",
    ],
  },
  {
    title: "DevOps",
    skills: [
      "Vite",
      "Webpack",
      "Git",
      "yarn workspaces",
      "монорепозитории",
      "npm-пакеты",
      "code splitting",
      "GitLab CI",
      "GitHub Actions",
      "Docker",
      "Docker Compose",
      "CI/CD",
    ],
  },
  {
    title: "Backend",
    skills: [
      "REST API",
      "GraphQL (Apollo Client)",
      "OpenAPI/Orval",
      "Kubb",
      "WebSocket",
      "Socket.io",
      "WebRTC",
      "Keycloak",
      "Nest.js",
      "TypeORM",
      "Drizzle ORM",
      "PostgreSQL",
      "Firebase",
      "Auth.js",
      "JWT/Passport",
      "Node.js",
      "Django REST",
      "Symfony",
      "Bitrix",
      "jQuery",
    ],
  },
  {
    title: "Качество",
    skills: ["Sentry", "Jest", "Vitest", "Playwright", "code review", "Scrum"],
  },
  {
    title: "UI & Продукт",
    skills: [
      "дизайн-системы",
      "UI Kit",
      "Material UI",
      "styled-components",
      "BEM",
      "i18next",
      "next-intl",
      "Telegram Mini Apps",
      "Figma",
    ],
  },
];

export const skillGroupsEn: SkillGroup[] = [
  {
    title: "Languages",
    skills: ["TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3/SCSS", "PHP", "Node.js", "Golang"],
  },
  {
    title: "Frontend",
    skills: [
      "React",
      "Next.js (SSR/SSG)",
      "Redux Toolkit",
      "Redux-Saga",
      "MobX",
      "Effector",
      "TanStack Query",
      "TanStack Table",
      "React Hook Form",
      "Zod",
      "Formik",
      "react-router",
      "Framer Motion",
      "Radix UI",
      "Tailwind CSS",
      "FSD",
    ],
  },
  {
    title: "Data visualization",
    skills: [
      "Cytoscape.js",
      "Highcharts",
      "Recharts",
      "react-grid-layout",
      "react-virtualized",
      "@tanstack/react-virtual",
      "Canvas",
      "Leaflet",
      "Yandex Maps",
    ],
  },
  {
    title: "DevOps",
    skills: [
      "Vite",
      "Webpack",
      "Git",
      "yarn workspaces",
      "monorepos",
      "npm packages",
      "code splitting",
      "GitLab CI",
      "GitHub Actions",
      "Docker",
      "Docker Compose",
      "CI/CD",
    ],
  },
  {
    title: "Backend",
    skills: [
      "REST API",
      "GraphQL (Apollo Client)",
      "OpenAPI/Orval",
      "Kubb",
      "WebSocket",
      "Socket.io",
      "WebRTC",
      "Keycloak",
      "Nest.js",
      "TypeORM",
      "Drizzle ORM",
      "PostgreSQL",
      "Firebase",
      "Auth.js",
      "JWT/Passport",
      "Node.js",
      "Django REST",
      "Symfony",
      "Bitrix",
      "jQuery",
    ],
  },
  {
    title: "Quality",
    skills: ["Sentry", "Jest", "Vitest", "Playwright", "code review", "Scrum"],
  },
  {
    title: "UI & Product",
    skills: [
      "design systems",
      "UI Kit",
      "Material UI",
      "styled-components",
      "BEM",
      "i18next",
      "next-intl",
      "Telegram Mini Apps",
      "Figma",
    ],
  },
];

export function getSkillGroups(locale: "ru" | "en"): SkillGroup[] {
  return locale === "en" ? skillGroupsEn : skillGroupsRu;
}

/** @deprecated use getSkillGroups */
export const skillGroups = skillGroupsRu;

export const highlightSkills = [
  "Next.js",
  "React",
  "TypeScript",
  "TanStack Query",
  "Orval",
  "Telegram Mini Apps",
  "Nest.js",
  "Playwright",
  "GraphQL",
  "Docker",
];
