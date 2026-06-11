export type SkillGroup = {
  title: string;
  skills: string[];
};

export const skillGroups: SkillGroup[] = [
  {
    title: "Языки",
    skills: ["TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3/SCSS"],
  },
  {
    title: "Frontend",
    skills: [
      "React",
      "Next.js (SSR/SSG)",
      "Redux Toolkit",
      "Redux-Saga",
      "MobX",
      "TanStack Query",
      "TanStack Table",
      "React Hook Form",
      "Zod",
      "Formik",
      "react-router",
      "Framer Motion",
      "Radix UI",
      "Tailwind CSS",
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
    ],
  },
  {
    title: "DevOps",
    skills: [
      "Vite",
      "Webpack",
      "Git",
      "монорепозитории",
      "code splitting",
      "dynamic imports",
      "tree shaking",
      "CI/CD",
      "GitHub Actions",
      "GitLab CI/CD",
      "Jenkins",
      "Docker",
      "Docker Compose",
      "Coolify",
    ],
  },
  {
    title: "Backend",
    skills: [
      "REST API",
      "GraphQL (Apollo Client)",
      "OpenAPI/Orval",
      "WebSocket",
      "Socket.io",
      "WebRTC",
      "Nest.js",
      "Drizzle ORM",
      "PostgreSQL",
      "Firebase",
      "Auth.js",
      "JWT/Passport",
      "Node.js",
      "Symfony",
      "Bitrix",
    ],
  },
  {
    title: "Качество",
    skills: ["Sentry", "Kibana", "Grafana", "Jest", "Vitest", "Playwright"],
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
      "Telegram Mini Apps",
      "Figma",
    ],
  },
];

export const highlightSkills = [
  "Next.js",
  "React",
  "TypeScript",
  "TanStack Query",
  "Orval",
  "Nest.js",
  "Telegram Mini Apps",
  "Playwright",
  "Docker",
  "GraphQL",
];
