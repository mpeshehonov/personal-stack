export type WorkBlock = {
  title: string;
  tagline: string;
  problem: string;
  contribution: string;
  stack: string[];
  outcomes: string[];
};

export type Experience = {
  company: string;
  role: string;
  period: string;
  location: string;
  /** Short scale/prestige line for recruiters (15s scan) */
  companyBlurb?: string;
  companyUrl?: string;
  blocks: WorkBlock[];
};

const aboutParagraphsRu = [
  "Senior Product Engineer (frontend-leaning), 7 лет: React, TypeScript, Next.js. Довожу сложные продуктовые UI до production: RBAC, длинные формы, OpenAPI/Orval, GraphQL/REST, WebSocket, CI/CD.",
  "Ownership end-to-end: контракт с backend, модули, code review, деплой, прод. Enterprise (X5, BI.ZONE, НЛМК, Citilink) и свои продукты (Mini Apps, seat maps, инструменты для стримеров).",
  "Ищу remote Senior Product / Frontend Engineer в продуктовой команде — роль с ownership, не «вёрстка по макету».",
];

const aboutParagraphsEn = [
  "Senior Product Engineer (frontend-leaning), 7 years: React, TypeScript, Next.js. I ship complex product UIs to production: RBAC, long forms, OpenAPI/Orval, GraphQL/REST, WebSocket, CI/CD.",
  "End-to-end ownership: API contracts, modules, review, deploy, production. Enterprise (X5, BI.ZONE, NLMK, Citilink) and product work (Mini Apps, seat maps, streamer tools).",
  "Looking for a remote Senior Product / Frontend Engineer role with product ownership — not pixel-pushing.",
];

const experiencesRu: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Senior Product Engineer",
    period: "09.2025 – 06.2026",
    location: "Удалённо",
    companyBlurb: "Product studio: ticketing и инструменты для стримеров",
    companyUrl: "https://potalonu.com",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Единственный FE: Mini App, кабинет, OBS overlay",
        problem: "Три клиента (кабинет, Mini App, OBS) должны жить на одном backend без рассинхрона.",
        contribution:
          "Единственный FE: собрал 3 React + Vite + TypeScript клиента, Orval/OpenAPI, WebSocket-алерты, GitHub Actions, Sentry.",
        stack: ["React", "TypeScript", "Vite", "Orval", "WebSocket", "GitHub Actions", "Sentry"],
        outcomes: [
          "End-to-end донат в production: Mini App → backend → кабинет → alert в OBS",
          "Три клиента на общих API-контрактах без рассинхрона FE/backend",
        ],
      },
      {
        title: "PREEGLOS",
        tagline: "Витрина билетов + seats.io-like редактор залов",
        problem: "Нужны checkout и свой редактор схем залов вместо seats.io.",
        contribution:
          "Next.js-витрина (Auth.js, PostgreSQL/Drizzle, Orval) + сервис залов и embed-виджет; GitLab CI, Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Замена seats.io в проде: десятки залов/событий, продажа мест через виджет",
          "Веб и Mini App на одной модели данных и API",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Senior Frontend Engineer",
    period: "04.2024 – 07.2025",
    location: "Удалённо",
    companyBlurb: "IT X5 Group, крупнейший продуктовый ритейлер РФ",
    companyUrl: "https://www.x5.ru",
    blocks: [
      {
        title: "НКЗ 3.0 — согласование закупок",
        tagline: "Enterprise-модуль для сотен (до тысяч) пользователей",
        problem: "Роли, статусы и многошаговое согласование в одном UI для внутренних пользователей.",
        contribution:
          "Один из 2 FE: Keycloak RBAC, react-hook-form, Orval/OpenAPI, UI Kit; сам перевёл модуль на Vite + code splitting.",
        stack: ["React", "TypeScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "Полный цикл UI согласования: роли, статусы, формы, переходы этапов",
          "Самостоятельная миграция на Vite ускорила разработку и проверки",
        ],
      },
    ],
  },
  {
    company: "BI.ZONE",
    role: "Senior Frontend Engineer",
    period: "06.2023 – 03.2024",
    location: "Удалённо",
    companyBlurb: "Кибербезопасность, продукты Threat Intelligence",
    companyUrl: "https://bi.zone",
    blocks: [
      {
        title: "Threat Intelligence",
        tagline: "Аналитика киберугроз, FE-команда 3 человека",
        problem: "Категории угроз, детальная карточка и связи в одном интерфейсе для аналитиков.",
        contribution:
          "Категории киберугроз и детальная форма для построения связей (GraphQL/Apollo); частично граф D3; виртуализация, Jest.",
        stack: ["React", "TypeScript", "GraphQL", "Apollo", "D3.js", "Jest"],
        outcomes: [
          "Категории и детальная форма стали основным способом связывать угрозы в продукте",
          "Виртуализация держала отзывчивость на больших списках",
        ],
      },
    ],
  },
  {
    company: "НЛМК",
    role: "Senior Frontend Engineer",
    period: "05.2022 – 06.2023",
    location: "Удалённо",
    companyBlurb: "Металлургия: digital на производстве",
    companyUrl: "https://nlmk.com",
    blocks: [
      {
        title: "Регистрация выпусков чугуна",
        tagline: "Production SPA вместо Excel",
        problem: "Цех вёл выпуски в Excel: потери данных и медленная фильтрация по сменам.",
        contribution:
          "React SPA: TanStack Table, React Query, Keycloak; GitLab CI, Sentry. Командировка на цех смотреть реальное использование.",
        stack: ["React", "TypeScript", "TanStack Table", "TanStack Query", "Keycloak", "Sentry"],
        outcomes: [
          "Цех перешёл на web как основной процесс (десятки пользователей на сменах)",
          "Sentry ускорил поиск и исправление ошибок в проде",
        ],
      },
    ],
  },
  {
    company: "Citilink",
    role: "Frontend Engineer",
    period: "04.2021 – 04.2022",
    location: "Удалённо",
    companyBlurb: "Крупный e-commerce электроники",
    companyUrl: "https://www.citilink.ru",
    blocks: [
      {
        title: "citilink.ru — каталог",
        tagline: "Миграция PHP/Symfony → Next.js",
        problem: "Перенос каталога на Next.js с фильтрами, SEO и REST к микросервисам.",
        contribution:
          "Зона каталога: фильтры, сортировка, пагинация, URL-state, microservice REST API; yarn workspaces, Jest.",
        stack: ["Next.js", "React", "TypeScript", "REST API", "Redux", "Jest"],
        outcomes: [
          "SEO сохранён: индексируемые страницы и фильтры в URL",
          "Фильтры и пагинация в URL работают и для розницы, и для оптового каталога",
        ],
      },
    ],
  },
];

const experiencesEn: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Senior Product Engineer",
    period: "Sep 2025 – Jun 2026",
    location: "Remote",
    companyBlurb: "Product studio: ticketing and streamer tools",
    companyUrl: "https://potalonu.com",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Sole FE: Mini App, dashboard, OBS overlay",
        problem: "Three clients (dashboard, Mini App, OBS) must stay in sync with one backend.",
        contribution:
          "Sole FE: built 3 React + Vite + TypeScript clients, Orval/OpenAPI, WebSocket alerts, GitHub Actions, Sentry.",
        stack: ["React", "TypeScript", "Vite", "Orval", "WebSocket", "GitHub Actions", "Sentry"],
        outcomes: [
          "End-to-end tip flow in production: Mini App → backend → dashboard → OBS alert",
          "Three clients on shared API contracts without FE/backend drift",
        ],
      },
      {
        title: "PREEGLOS",
        tagline: "Ticket storefront + seats.io-like hall editor",
        problem: "Needed checkout and an in-house hall editor instead of seats.io.",
        contribution:
          "Next.js storefront (Auth.js, PostgreSQL/Drizzle, Orval) + hall service and embed widget; GitLab CI, Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Production seats.io alternative: dozens of halls/events via embed widget",
          "Web and Mini App on one data model and API",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Senior Frontend Engineer",
    period: "Apr 2024 – Jul 2025",
    location: "Remote",
    companyBlurb: "IT for X5 Group, Russia’s largest grocery retailer",
    companyUrl: "https://www.x5.ru",
    blocks: [
      {
        title: "NKZ 3.0 — procurement approval",
        tagline: "Enterprise module for hundreds (up to thousands) of users",
        problem: "Roles, statuses, and multi-step approval in one UI for internal users.",
        contribution:
          "One of 2 FE: Keycloak RBAC, react-hook-form, Orval/OpenAPI, UI Kit; owned full Vite migration + code splitting.",
        stack: ["React", "TypeScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "Full approval UI cycle: roles, statuses, forms, stage transitions",
          "Solo Vite migration sped up development and checks",
        ],
      },
    ],
  },
  {
    company: "BI.ZONE",
    role: "Senior Frontend Engineer",
    period: "Jun 2023 – Mar 2024",
    location: "Remote",
    companyBlurb: "Cybersecurity — Threat Intelligence products",
    companyUrl: "https://bi.zone",
    blocks: [
      {
        title: "Threat Intelligence",
        tagline: "Cyber threat analytics, FE team of 3",
        problem: "Threat categories, detail cards, and relationships in one workspace for analysts.",
        contribution:
          "Threat-category sections and detail form for relationships (GraphQL/Apollo); partial D3 graph; virtualization, Jest.",
        stack: ["React", "TypeScript", "GraphQL", "Apollo", "D3.js", "Jest"],
        outcomes: [
          "Categories and detail form became the main way to link threats in the product",
          "Virtualization kept large entity lists responsive",
        ],
      },
    ],
  },
  {
    company: "NLMK",
    role: "Senior Frontend Engineer",
    period: "May 2022 – Jun 2023",
    location: "Remote",
    companyBlurb: "Steel industry: digital tools for plant production",
    companyUrl: "https://nlmk.com",
    blocks: [
      {
        title: "Cast iron release registration",
        tagline: "Production SPA replacing Excel",
        problem: "Plant teams tracked releases in Excel: data loss and slow shift filtering.",
        contribution:
          "React SPA: TanStack Table, React Query, Keycloak; GitLab CI, Sentry. Plant visit to observe real shift usage.",
        stack: ["React", "TypeScript", "TanStack Table", "TanStack Query", "Keycloak", "Sentry"],
        outcomes: [
          "Plant teams moved to web as the primary process (dozens of shift users)",
          "Sentry sped up finding and fixing production errors",
        ],
      },
    ],
  },
  {
    company: "Citilink",
    role: "Frontend Engineer",
    period: "Apr 2021 – Apr 2022",
    location: "Remote",
    companyBlurb: "Large electronics e-commerce",
    companyUrl: "https://www.citilink.ru",
    blocks: [
      {
        title: "citilink.ru — catalog",
        tagline: "Migration PHP/Symfony → Next.js",
        problem: "Move catalog to Next.js with filters, SEO, and microservice REST.",
        contribution:
          "Catalog scope: filters, sort, pagination, URL state, microservice REST API; yarn workspaces, Jest.",
        stack: ["Next.js", "React", "TypeScript", "REST API", "Redux", "Jest"],
        outcomes: [
          "SEO preserved: indexable pages and filters in the URL",
          "URL-synced filters and pagination for both retail and B2B catalog views",
        ],
      },
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
