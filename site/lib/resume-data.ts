export type Experience = {
  company: string;
  role: string;
  period: string;
  location: string;
  projects?: { name: string; stack: string; bullets: string[] }[];
  bullets?: string[];
};

const aboutParagraphsRu = [
  "Senior Frontend / Fullstack разработчик. Веб с 2018 года: B2B, e-commerce, маркетплейсы, real-time, Telegram Mini Apps. Делаю интерфейсы со сложными сценариями, RBAC, Orval/OpenAPI и интеграциями REST, GraphQL, WebSocket.",
  "Работал в X5 Tech, НЛМК, BI.ZONE, Citilink и продуктовых командах. Полный список кейсов — на сайте в разделе «Проекты» и по запросу.",
];

const aboutParagraphsEn = [
  "Senior Frontend / Fullstack engineer since 2018: B2B, e-commerce, marketplaces, real-time, Telegram Mini Apps. Complex flows, RBAC, Orval/OpenAPI, REST, GraphQL, and WebSocket integrations.",
  "Experience at X5 Tech, NLMK, BI.ZONE, Citilink, and product teams. Full case list on the Projects page and on request.",
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
          "monolith: веб-кабинет, Mini App и websocket-pages для OBS — три клиента, один backend",
          "Orval по OpenAPI, очередь алертов на WebSocket с reconnect и preload медиа",
          "Кабинет: CRUD коллекций, настройки алертов, debounce-поиск",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "potalonu-frontend: витрина, покупка билетов, Telegram Mini App, Chart.js",
          "seatmap-studio: редактор залов, embed `/embed/[hallId]`, события и бронирования",
          "Self-hosted: Docker Compose, GitLab CI/CD, stage на nginx",
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
      "Модуль согласования закупок (НКЗ 3.0): RBAC, статусы, переходы, черновики",
      "Keycloak: SSO и матрица доступа к модулям",
      "Orval по OpenAPI — без ручного обновления контрактов",
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
      "Граф связей на Cytoscape.js, фильтры для аналитиков",
      "Дашборды: Highcharts, Recharts, react-grid-layout, виртуализация списков",
    ],
  },
  {
    company: "НЛМК",
    role: "Frontend-разработчик",
    period: "05.2022 – 06.2023",
    location: "Удалённо",
    bullets: [
      "«Регистрация выпусков чугуна» — единый интерфейс вместо ручных форм",
      "Keycloak: SSO, роли, защита API",
      "TanStack Table + React Query на больших объёмах данных",
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
      "Фильтры, сортировка, пагинация, состояние в URL",
      "Согласование REST API с backend и микросервисами",
      "Конверсия каталога выросла примерно на 15% после миграции",
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
          "monolith: web dashboard, Mini App, and websocket-pages for OBS — three clients, one backend",
          "Orval from OpenAPI, WebSocket alert queue with reconnect and media preload",
          "Dashboard: CRUD collections, alert settings, debounced search",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "potalonu-frontend: storefront, checkout, Telegram Mini App, Chart.js",
          "seatmap-studio: hall editor, embed `/embed/[hallId]`, events and bookings",
          "Self-hosted: Docker Compose, GitLab CI/CD, nginx stage",
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
      "Procurement approval module (NKZ 3.0): RBAC, statuses, transitions, drafts",
      "Keycloak SSO and module access matrix",
      "Orval from OpenAPI — no manual contract updates",
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
      "Relationship graphs on Cytoscape.js, analyst filters",
      "Dashboards: Highcharts, Recharts, react-grid-layout, virtualized lists",
    ],
  },
  {
    company: "NLMK",
    role: "Frontend engineer",
    period: "May 2022 – Jun 2023",
    location: "Remote",
    bullets: [
      "Cast iron release registration — one UI instead of manual forms",
      "Keycloak SSO, roles, protected API routes",
      "TanStack Table + React Query on large datasets",
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
      "Filters, sort, pagination, URL state",
      "REST API alignment with backend and microservices",
      "Catalog conversion improved by roughly 15% after migration",
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
