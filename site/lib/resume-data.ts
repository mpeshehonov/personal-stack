export type Experience = {
  company: string;
  role: string;
  period: string;
  location: string;
  projects?: { name: string; stack: string; bullets: string[] }[];
  bullets?: string[];
};

const aboutParagraphsRu = [
  "Frontend / Fullstack разработчик с 2018 года, уровень Senior. B2B, e-commerce, маркетплейсы, real-time, Telegram Mini Apps. Делаю интерфейсы со сложными сценариями, RBAC, Orval/OpenAPI и интеграциями REST, GraphQL, WebSocket.",
  "Работал в X5 Tech, НЛМК, BI.ZONE, Citilink и продуктовых командах. Полный список кейсов — на сайте в разделе «Проекты» и по запросу.",
];

const aboutParagraphsEn = [
  "Frontend / Fullstack engineer since 2018, Senior level. B2B, e-commerce, marketplaces, real-time, Telegram Mini Apps. Complex flows, RBAC, Orval/OpenAPI, REST, GraphQL, and WebSocket integrations.",
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
          "Три клиента: кабинет стримера, Telegram Mini App и overlay для OBS",
          "Донаты в Mini App: оплата, REST через Orval, кабинет с коллекциями и алертами",
          "Overlay в эфире: WebSocket, очередь алертов, reconnect, TTS и анимации",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Витрина событий, покупка билетов, Telegram Mini App",
          "Редактор схем залов и виджет выбора мест для сайтов партнёров",
          "Docker + GitLab CI/CD, stage на nginx",
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
      "Модуль согласования закупок (НКЗ 3.0): роли, статусы, переходы, черновики",
      "Keycloak: SSO и матрица доступа к модулям",
      "Orval по OpenAPI — типы и клиент без ручных правок контрактов",
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
      "Приложение «Регистрация выпусков чугуна» — единый интерфейс вместо Excel и форм",
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
      "После миграции каталог стал быстрее и удобнее для покупателей",
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
          "Three clients: streamer dashboard, Telegram Mini App, and OBS overlay",
          "Donations in Mini App: checkout, Orval REST client, dashboard with collections and alerts",
          "Live overlay: WebSocket alert queue, reconnect, TTS, and animations",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Event storefront, ticket checkout, Telegram Mini App",
          "Hall layout editor and seat picker widget for partner sites",
          "Docker + GitLab CI/CD, nginx stage environment",
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
      "Procurement approval module (NKZ 3.0): roles, statuses, transitions, drafts",
      "Keycloak SSO and module access matrix",
      "Orval from OpenAPI — typed client without manual contract updates",
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
      "Cast iron release registration app — one UI instead of spreadsheets and forms",
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
      "Catalog became faster and easier to use after migration",
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
