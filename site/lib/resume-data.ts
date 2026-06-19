export type Experience = {
  company: string;
  role: string;
  period: string;
  location: string;
  projects?: { name: string; stack: string; bullets: string[] }[];
  bullets?: string[];
};

const aboutParagraphsRu = [
  "Frontend / Fullstack с 2018 года, уровень Senior. B2B, e-commerce, real-time, Telegram Mini Apps. Сложные UI, RBAC, проектирование API, Orval/OpenAPI, REST, GraphQL, WebSocket.",
  "Готов к выходу на проект ASAP. Кейсы: X5 Tech, НЛМК, BI.ZONE, Citilink, POTALONU. Полный список на сайте в разделе Проекты.",
];

const aboutParagraphsEn = [
  "Frontend / Fullstack engineer since 2018, Senior level. B2B, e-commerce, real-time, Telegram Mini Apps. Complex UI, API design, Orval/OpenAPI, REST, GraphQL, WebSocket.",
  "Available to start ASAP. Cases: X5 Tech, NLMK, BI.ZONE, Citilink, POTALONU. Full list on the Projects page.",
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
          "Три клиента на React 19: кабинет, Telegram Mini App, OBS overlay",
          "Общие npm-пакеты UI и утилит между Mini App и веб-кабинетом",
          "GitHub Actions: lint, build, деплой; REST через Orval, WebSocket overlay",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Витрина, checkout, Telegram Mini App, редактор схем залов",
          "GitLab CI/CD: test, build, stage на nginx; Docker Compose",
          "Согласовывал REST API с backend, typed клиент через OpenAPI",
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
      "Внутренние npm-пакеты UI Kit и shared types; Scrum, code review, груминг постановок",
      "Orval по OpenAPI: проектирование и синхронизация REST контрактов с backend",
      "Vite: code splitting, useMemo/useCallback на тяжёлых формах и таблицах",
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend-разработчик",
    period: "06.2023 – 03.2024",
    location: "Удалённо",
    bullets: [
      "Thread Intelligence: GraphQL (Apollo), MobX, React Query, Orval",
      "Внутренние npm-пакеты @bizone; графы Cytoscape.js, дашборды, виртуализация",
      "Оптимизация рендера: lazy loading, react-virtualized, Chrome DevTools profiling",
      "Code review, разбор чужого кода, unit-тесты на Jest",
    ],
  },
  {
    company: "НЛМК",
    role: "Frontend-разработчик",
    period: "05.2022 – 06.2023",
    location: "Удалённо",
    bullets: [
      "SPA регистрации выпусков чугуна вместо Excel и разрозненных форм",
      "GitLab CI: lint, test, build на merge request; Keycloak SSO и RBAC",
      "Внутренние npm-пакеты shared UI и утилит; TanStack Table + React Query",
      "Sentry, Jest unit-тесты на бизнес-логику таблиц и фильтров",
    ],
  },
  {
    company: "Citilink",
    role: "Frontend-разработчик",
    period: "04.2021 – 04.2022",
    location: "Удалённо",
    bullets: [
      "Монорепозиторий yarn workspaces: каталог, главная, shared npm-пакеты",
      "Миграция каталога и главной с PHP/Symfony на Next.js (SSR, адаптивная верстка)",
      "Проектирование REST API с backend и микросервисами; Redux на каталоге",
      "Jest unit-тесты, code review в Scrum-команде e-commerce",
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
          "Three React 19 clients: dashboard, Telegram Mini App, OBS overlay",
          "Shared npm packages for UI and utils across Mini App and web dashboard",
          "GitHub Actions: lint, build, deploy; Orval REST client, WebSocket overlay",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Storefront, checkout, Telegram Mini App, hall layout editor",
          "GitLab CI/CD: test, build, nginx stage; Docker Compose",
          "REST API design with backend, typed client via OpenAPI",
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
      "Internal npm packages for UI kit and shared types; Scrum, code review, grooming",
      "Orval from OpenAPI: REST contract design and sync with backend",
      "Vite code splitting; useMemo/useCallback on heavy forms and tables",
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend engineer",
    period: "Jun 2023 – Mar 2024",
    location: "Remote",
    bullets: [
      "Thread Intelligence: GraphQL (Apollo), MobX, React Query, Orval",
      "Internal @bizone npm packages; Cytoscape.js graphs, dashboards, virtualization",
      "Render optimization: lazy loading, react-virtualized, Chrome DevTools profiling",
      "Code review, legacy code navigation, Jest unit tests",
    ],
  },
  {
    company: "NLMK",
    role: "Frontend engineer",
    period: "May 2022 – Jun 2023",
    location: "Remote",
    bullets: [
      "Cast iron release SPA replacing spreadsheets and scattered forms",
      "GitLab CI: lint, test, build on merge requests; Keycloak SSO and RBAC",
      "Internal npm packages for shared UI and utils; TanStack Table + React Query",
      "Sentry, Jest unit tests on table and filter business logic",
    ],
  },
  {
    company: "Citilink",
    role: "Frontend engineer",
    period: "Apr 2021 – Apr 2022",
    location: "Remote",
    bullets: [
      "Yarn workspaces monorepo: catalog, homepage, shared npm packages",
      "Migrated catalog and homepage from PHP/Symfony to Next.js (SSR, responsive layout)",
      "REST API design with backend and microservices; Redux on catalog",
      "Jest unit tests, code review in Scrum e-commerce team",
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
