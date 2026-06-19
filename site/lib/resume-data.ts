export type Experience = {
  company: string;
  role: string;
  period: string;
  location: string;
  projects?: { name: string; stack: string; bullets: string[] }[];
  bullets?: string[];
};

const aboutParagraphsRu = [
  "Frontend / Fullstack с 2018 года, уровень Senior. B2B, e-commerce, real-time, Telegram Mini Apps. Сложные UI, RBAC, Orval/OpenAPI, REST, GraphQL, WebSocket.",
  "Готов к выходу ASAP. Кейсы на mpeshekhonov.ru в разделе Проекты, полный список по запросу.",
];

const aboutParagraphsEn = [
  "Frontend / Fullstack engineer since 2018, Senior level. B2B, e-commerce, real-time, Telegram Mini Apps. Complex UI, RBAC, Orval/OpenAPI, REST, GraphQL, WebSocket.",
  "Available to start ASAP. Case studies at mpeshekhonov.ru/projects.",
];

const experiencesRu: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Fullstack / Frontend-разработчик",
    period: "09.2025 – н.в.",
    location: "Удалённо",
    projects: [
      {
        name: "sendonate.com",
        stack: "React, Vite, Telegram Mini App, WebSocket, Orval, Django REST",
        bullets: [
          "Три клиента: кабинет стримера, Telegram Mini App, OBS overlay",
          "Mini App: оплата донатов, REST через Orval; overlay в эфире на WebSocket",
          "GitHub Actions для lint, build и деплоя",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Витрина событий, checkout, Telegram Mini App",
          "Редактор схем залов на Canvas/SVG и виджет выбора мест для сайтов партнёров",
          "GitLab CI/CD, Docker Compose; REST через Orval",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Frontend-разработчик",
    period: "04.2024 – 07.2025",
    location: "Удалённо",
    bullets: [
      "Модуль согласования закупок (НКЗ 3.0): RBAC, статусы, длинные цепочки согласования",
      "Keycloak SSO, Orval по OpenAPI, формы на react-hook-form",
      "Внутренние npm-пакеты UI Kit; Scrum, code review",
      "Vite: code splitting на длинных сценариях согласования",
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend-разработчик",
    period: "06.2023 – 03.2024",
    location: "Удалённо",
    bullets: [
      "Thread Intelligence: GraphQL (Apollo), MobX, React Query, Orval",
      "Граф связей на Cytoscape.js, дашборды, виртуализация списков",
      "Внутренние npm-пакеты @bizone; Jest unit-тесты",
      "Code review, разбор чужого кода",
    ],
  },
  {
    company: "НЛМК",
    role: "Frontend-разработчик",
    period: "05.2022 – 06.2023",
    location: "Удалённо",
    bullets: [
      "Приложение регистрации выпусков чугуна вместо Excel и разрозненных форм",
      "TanStack Table + React Query на больших объёмах данных",
      "GitLab CI на MR; Keycloak SSO и RBAC; внутренние npm-пакеты shared UI",
      "Sentry в продакшене",
    ],
  },
  {
    company: "Citilink",
    role: "Frontend-разработчик",
    period: "04.2021 – 04.2022",
    location: "Удалённо",
    bullets: [
      "Миграция каталога и главной с PHP/Symfony на Next.js",
      "Монорепозиторий yarn workspaces, shared npm-пакеты",
      "Фильтры, сортировка, пагинация, состояние в URL",
      "REST API с backend и микросервисами; Redux, Jest, code review",
    ],
  },
];

const experiencesEn: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Fullstack / Frontend engineer",
    period: "Sep 2025 – present",
    location: "Remote",
    projects: [
      {
        name: "sendonate.com",
        stack: "React, Vite, Telegram Mini App, WebSocket, Orval, Django REST",
        bullets: [
          "Three clients: streamer dashboard, Telegram Mini App, OBS overlay",
          "Mini App checkout, Orval REST client; live WebSocket overlay",
          "GitHub Actions for lint, build, and deploy",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Event storefront, checkout, Telegram Mini App",
          "Hall layout editor on Canvas/SVG and seat picker widget for partner sites",
          "GitLab CI/CD, Docker Compose; Orval REST client",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Frontend engineer",
    period: "Apr 2024 – Jul 2025",
    location: "Remote",
    bullets: [
      "Procurement approval (NKZ 3.0): RBAC, statuses, long approval chains",
      "Keycloak SSO, Orval from OpenAPI, react-hook-form",
      "Internal npm packages for UI kit; Scrum, code review",
      "Vite code splitting on long approval flows",
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend engineer",
    period: "Jun 2023 – Mar 2024",
    location: "Remote",
    bullets: [
      "Thread Intelligence: GraphQL (Apollo), MobX, React Query, Orval",
      "Relationship graphs on Cytoscape.js, dashboards, virtualized lists",
      "Internal @bizone npm packages; Jest unit tests",
      "Code review, legacy code navigation",
    ],
  },
  {
    company: "NLMK",
    role: "Frontend engineer",
    period: "May 2022 – Jun 2023",
    location: "Remote",
    bullets: [
      "Cast iron release app replacing spreadsheets and scattered forms",
      "TanStack Table + React Query on large datasets",
      "GitLab CI on MR; Keycloak SSO and RBAC; internal shared UI npm packages",
      "Sentry in production",
    ],
  },
  {
    company: "Citilink",
    role: "Frontend engineer",
    period: "Apr 2021 – Apr 2022",
    location: "Remote",
    bullets: [
      "Migrated catalog and homepage from PHP/Symfony to Next.js",
      "Yarn workspaces monorepo, shared npm packages",
      "Filters, sort, pagination, URL state",
      "REST API with backend and microservices; Redux, Jest, code review",
    ],
  },
];

export const education = [
  {
    school: "Тульский государственный коммунально-строительный техникум",
    schoolEn: "Tula State Communal Construction College",
    field: "Земельно-имущественные отношения",
    fieldEn: "Land and property relations",
    period: "2015 – 2018",
    location: "Тула, Россия",
    locationEn: "Tula, Russia",
  },
  {
    school: "Компьютерная академия «ШАГ»",
    schoolEn: "Computer Academy STEP",
    field: "Веб-разработка",
    fieldEn: "Web development",
    period: "2016",
    location: "Тула, Россия",
    locationEn: "Tula, Russia",
  },
];

const achievementsRu =
  "Победитель хакатона «Цифровой прорыв» (2021, 2020), победитель Hack.Genesis _ONLINE_, финалист Virus Hack, эксперт чемпионата WorldSkills.";

const achievementsEn =
  "Winner of Digital Breakthrough hackathon (2021, 2020), Hack.Genesis _ONLINE_, Virus Hack finalist, WorldSkills championship expert.";

export function getExperiences(locale: "ru" | "en"): Experience[] {
  return locale === "en" ? experiencesEn : experiencesRu;
}

export function getAboutParagraphs(locale: "ru" | "en"): string[] {
  return locale === "en" ? aboutParagraphsEn : aboutParagraphsRu;
}

/** @deprecated use getAboutParagraphs */
export function getAboutText(locale: "ru" | "en"): string {
  return getAboutParagraphs(locale).join("\n\n");
}

export function getAchievements(locale: "ru" | "en"): string {
  return locale === "en" ? achievementsEn : achievementsRu;
}

export function getEducation(locale: "ru" | "en") {
  return education.map((edu) => ({
    school: locale === "en" ? edu.schoolEn : edu.school,
    field: locale === "en" ? edu.fieldEn : edu.field,
    period: edu.period,
    location: locale === "en" ? edu.locationEn : edu.location,
  }));
}
