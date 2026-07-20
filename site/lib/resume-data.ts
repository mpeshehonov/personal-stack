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
  "Senior Product / Frontend Engineer, 7 лет. React, TypeScript, Next.js. Довожу сложные интерфейсы до production: роли и доступы, длинные формы, REST и GraphQL, WebSocket, CI/CD.",
  "Беру задачу от контракта с backend до деплоя и поддержки в проде. Крупный enterprise (X5, BI.ZONE, НЛМК, Citilink) и продуктовая студия (Mini Apps, схемы залов, инструменты для стримеров).",
  "Ищу remote-роль, где нужен сильный frontend с ответственностью за модуль, а не только вёрстка по макету.",
];

const aboutParagraphsEn = [
  "Senior Product / Frontend Engineer, 7 years. React, TypeScript, Next.js. I ship complex product UIs to production: roles and access, long forms, REST and GraphQL, WebSocket, CI/CD.",
  "I take work from backend contract through deploy and production support. Enterprise (X5, BI.ZONE, NLMK, Citilink) and product studio work (Mini Apps, hall layouts, streamer tools).",
  "Looking for a remote role that needs strong frontend with module ownership, not layout-only work.",
];

const experiencesRu: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Senior Product Engineer",
    period: "09.2025 - 06.2026",
    location: "Удалённо",
    companyBlurb: "Продуктовая студия: билеты и инструменты для стримеров",
    companyUrl: "https://potalonu.com",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Единственный frontend: Mini App, кабинет, OBS-оверлей",
        problem: "Три клиента (кабинет, Mini App, OBS) должны жить на одном backend без рассинхрона.",
        contribution:
          "Единственный frontend: собрал 3 клиента на React, Vite и TypeScript, Orval по OpenAPI, WebSocket-алерты, GitHub Actions, Sentry.",
        stack: ["React", "TypeScript", "Vite", "Orval", "WebSocket", "GitHub Actions", "Sentry"],
        outcomes: [
          "Собрал 3 клиента на React, Vite и TypeScript и довёл поток доната до production",
          "Подключил typed API из OpenAPI (Orval) и WebSocket-алерты с очередью и reconnect",
          "Настроил GitHub Actions и Sentry: три клиента на одном контракте без рассинхрона с backend",
          "Закрыл полный сценарий: Mini App, backend, кабинет, алерт в OBS",
        ],
      },
      {
        title: "PREEGLOS",
        tagline: "Витрина билетов и редактор схем залов",
        problem: "Нужны checkout и свой редактор схем залов вместо seats.io.",
        contribution:
          "Next.js-витрина (Auth.js, PostgreSQL/Drizzle, Orval) плюс сервис залов и embed-виджет; GitLab CI, Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Собрал Next.js checkout: Auth.js, PostgreSQL/Drizzle, Orval по OpenAPI",
          "Сделал сервис схем залов и embed-виджет выбора мест вместо seats.io",
          "В проде: десятки залов и событий, продажа мест без ручной отрисовки схем",
          "Настроил GitLab CI и Docker Compose для выкладки",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Senior Frontend Engineer",
    period: "04.2024 - 07.2025",
    location: "Удалённо",
    companyBlurb: "IT X5 Group, крупнейший продуктовый ритейлер РФ",
    companyUrl: "https://www.x5.ru",
    blocks: [
      {
        title: "НКЗ 3.0 - согласование закупок",
        tagline: "Модуль для сотен (до тысяч) внутренних пользователей",
        problem: "Роли, статусы и многошаговое согласование в одном UI для внутренних пользователей.",
        contribution:
          "Один из 2 frontend: Keycloak, react-hook-form, Orval по OpenAPI, UI Kit; сам перевёл модуль на Vite с code splitting.",
        stack: ["React", "TypeScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "Один из 2 frontend: роли через Keycloak, многошаговые формы, Orval по OpenAPI, UI Kit",
          "Сам перевёл модуль на Vite с code splitting на длинных сценариях",
          "Закрыл UI полного цикла согласования: роли, статусы, формы, переходы этапов",
          "Вёл code review и декомпозицию модулей вместе с backend",
        ],
      },
    ],
  },
  {
    company: "BI.ZONE",
    role: "Senior Frontend Engineer",
    period: "06.2023 - 03.2024",
    location: "Удалённо",
    companyBlurb: "Кибербезопасность, продукты Threat Intelligence",
    companyUrl: "https://bi.zone",
    blocks: [
      {
        title: "Threat Intelligence",
        tagline: "Аналитика киберугроз, frontend-команда из 3 человек",
        problem: "Категории угроз, детальная карточка и связи в одном интерфейсе для аналитиков.",
        contribution:
          "Разделы категорий угроз и детальная форма связей на GraphQL/Apollo; граф на D3; виртуализация, Jest.",
        stack: ["React", "TypeScript", "GraphQL", "Apollo", "D3.js", "Jest"],
        outcomes: [
          "Собрал разделы категорий угроз и детальную форму связей на GraphQL и Apollo",
          "Добавил виртуализацию длинных списков; покрыл Jest; вёл code review",
          "Категории и форма стали основным способом связывать угрозы в продукте",
          "Участвовал в графе связей сущностей на D3.js",
        ],
      },
    ],
  },
  {
    company: "НЛМК",
    role: "Senior Frontend Engineer",
    period: "05.2022 - 06.2023",
    location: "Удалённо",
    companyBlurb: "Металлургия: digital на производстве",
    companyUrl: "https://nlmk.com",
    blocks: [
      {
        title: "Регистрация выпусков чугуна",
        tagline: "SPA вместо Excel",
        problem: "Цех вёл выпуски в Excel: потери данных и медленная фильтрация по сменам.",
        contribution:
          "React SPA: TanStack Table, React Query, Keycloak; GitLab CI, Sentry. Командировка на цех под реальный сценарий смены.",
        stack: ["React", "TypeScript", "TanStack Table", "TanStack Query", "Keycloak", "Sentry"],
        outcomes: [
          "Заменил Excel на React SPA: TanStack Table, React Query, Keycloak",
          "Съездил на цех, посмотрел реальный сценарий смены и учёл его в UI",
          "Цех перешёл на web как основной процесс (десятки пользователей на сменах)",
          "Подключил Sentry и GitLab CI: быстрее находил и чинил ошибки в проде",
        ],
      },
    ],
  },
  {
    company: "Citilink",
    role: "Frontend Engineer",
    period: "04.2021 - 04.2022",
    location: "Удалённо",
    companyBlurb: "Крупный e-commerce электроники",
    companyUrl: "https://www.citilink.ru",
    blocks: [
      {
        title: "citilink.ru - каталог",
        tagline: "Миграция с PHP/Symfony на Next.js",
        problem: "Перенос каталога на Next.js с фильтрами, SEO и REST к микросервисам.",
        contribution:
          "Зона каталога: фильтры, сортировка, пагинация, состояние в URL, REST к микросервисам; yarn workspaces, Jest.",
        stack: ["Next.js", "React", "TypeScript", "REST API", "Redux", "Jest"],
        outcomes: [
          "Перенёс зону каталога: фильтры, сортировка, пагинация, состояние в URL, REST к микросервисам",
          "Сохранил SEO: страницы и фильтры индексируются через URL",
          "Одно URL-состояние фильтров работает и для розницы, и для оптового каталога",
          "Yarn workspaces, Jest, code review",
        ],
      },
    ],
  },
];

const experiencesEn: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Senior Product Engineer",
    period: "Sep 2025 - Jun 2026",
    location: "Remote",
    companyBlurb: "Product studio: ticketing and streamer tools",
    companyUrl: "https://potalonu.com",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Sole frontend: Mini App, dashboard, OBS overlay",
        problem: "Three clients (dashboard, Mini App, OBS) must stay in sync with one backend.",
        contribution:
          "Sole frontend: built 3 React, Vite, and TypeScript clients, Orval from OpenAPI, WebSocket alerts, GitHub Actions, Sentry.",
        stack: ["React", "TypeScript", "Vite", "Orval", "WebSocket", "GitHub Actions", "Sentry"],
        outcomes: [
          "Built 3 React, Vite, and TypeScript clients and shipped the tip flow to production",
          "Wired typed API from OpenAPI (Orval) and WebSocket alerts with queue and reconnect",
          "Set up GitHub Actions and Sentry: three clients on one contract without FE/backend drift",
          "Closed the full path: Mini App, backend, dashboard, alert in OBS",
        ],
      },
      {
        title: "PREEGLOS",
        tagline: "Ticket storefront and hall layout editor",
        problem: "Needed checkout and an in-house hall editor instead of seats.io.",
        contribution:
          "Next.js storefront (Auth.js, PostgreSQL/Drizzle, Orval) plus hall service and embed widget; GitLab CI, Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Built Next.js checkout: Auth.js, PostgreSQL/Drizzle, Orval from OpenAPI",
          "Built hall layout service and embed seat picker instead of seats.io",
          "In production: dozens of halls and events, seat sales without hand-drawn layouts",
          "Set up GitLab CI and Docker Compose for delivery",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Senior Frontend Engineer",
    period: "Apr 2024 - Jul 2025",
    location: "Remote",
    companyBlurb: "IT for X5 Group, Russia's largest grocery retailer",
    companyUrl: "https://www.x5.ru",
    blocks: [
      {
        title: "NKZ 3.0 - procurement approval",
        tagline: "Module for hundreds (up to thousands) of internal users",
        problem: "Roles, statuses, and multi-step approval in one UI for internal users.",
        contribution:
          "One of 2 frontend engineers: Keycloak, react-hook-form, Orval from OpenAPI, UI Kit; owned the Vite migration with code splitting.",
        stack: ["React", "TypeScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "One of 2 frontend engineers: Keycloak roles, multi-step forms, Orval from OpenAPI, UI Kit",
          "Owned the Vite migration with code splitting on long flows",
          "Covered the full approval UI cycle: roles, statuses, forms, stage transitions",
          "Ran code review and module breakdown with backend",
        ],
      },
    ],
  },
  {
    company: "BI.ZONE",
    role: "Senior Frontend Engineer",
    period: "Jun 2023 - Mar 2024",
    location: "Remote",
    companyBlurb: "Cybersecurity - Threat Intelligence products",
    companyUrl: "https://bi.zone",
    blocks: [
      {
        title: "Threat Intelligence",
        tagline: "Cyber threat analytics, frontend team of 3",
        problem: "Threat categories, detail cards, and relationships in one workspace for analysts.",
        contribution:
          "Threat-category sections and detail form for relationships on GraphQL/Apollo; D3 graph; virtualization, Jest.",
        stack: ["React", "TypeScript", "GraphQL", "Apollo", "D3.js", "Jest"],
        outcomes: [
          "Built threat-category sections and a detail form for relationships on GraphQL and Apollo",
          "Added list virtualization; covered with Jest; ran code review",
          "Categories and the detail form became the main way to link threats in the product",
          "Contributed to the entity relationship graph on D3.js",
        ],
      },
    ],
  },
  {
    company: "NLMK",
    role: "Senior Frontend Engineer",
    period: "May 2022 - Jun 2023",
    location: "Remote",
    companyBlurb: "Steel industry: digital tools for plant production",
    companyUrl: "https://nlmk.com",
    blocks: [
      {
        title: "Cast iron release registration",
        tagline: "SPA replacing Excel",
        problem: "Plant teams tracked releases in Excel: data loss and slow shift filtering.",
        contribution:
          "React SPA: TanStack Table, React Query, Keycloak; GitLab CI, Sentry. Plant visit under the real shift scenario.",
        stack: ["React", "TypeScript", "TanStack Table", "TanStack Query", "Keycloak", "Sentry"],
        outcomes: [
          "Replaced Excel with a React SPA: TanStack Table, React Query, Keycloak",
          "Visited the plant, watched the real shift flow, and reflected it in the UI",
          "Plant teams moved to web as the primary process (dozens of shift users)",
          "Wired Sentry and GitLab CI: faster to find and fix production errors",
        ],
      },
    ],
  },
  {
    company: "Citilink",
    role: "Frontend Engineer",
    period: "Apr 2021 - Apr 2022",
    location: "Remote",
    companyBlurb: "Large electronics e-commerce",
    companyUrl: "https://www.citilink.ru",
    blocks: [
      {
        title: "citilink.ru - catalog",
        tagline: "Migration from PHP/Symfony to Next.js",
        problem: "Move catalog to Next.js with filters, SEO, and microservice REST.",
        contribution:
          "Catalog scope: filters, sort, pagination, URL state, REST to microservices; yarn workspaces, Jest.",
        stack: ["Next.js", "React", "TypeScript", "REST API", "Redux", "Jest"],
        outcomes: [
          "Moved the catalog zone: filters, sort, pagination, URL state, REST to microservices",
          "Kept SEO: pages and filters stay indexable via the URL",
          "One URL filter state works for both retail and wholesale catalog views",
          "Yarn workspaces, Jest, code review",
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
    period: "2015 - 2018",
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
