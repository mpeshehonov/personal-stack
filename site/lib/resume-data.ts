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
  blocks: WorkBlock[];
};

const aboutParagraphsRu = [
  "Senior Frontend-разработчик, 7+ лет коммерческой разработки. React, TypeScript, Next.js: e-commerce, enterprise-модули, маркетплейсы. REST API, Git, code review, Scrum/Agile.",
  "Другие задачи и кейсы — в разделе Проекты на сайте. Fullstack: Django REST, Nest.js, PostgreSQL, SQL. Готов к выходу ASAP.",
];

const aboutParagraphsEn = [
  "Senior Frontend engineer, 7+ years in commercial development. React, TypeScript, Next.js: e-commerce, enterprise modules, marketplaces. REST API, Git, code review, Scrum/Agile.",
  "Other work and case studies — in the Projects section on the site. Fullstack: Django REST, Nest.js, PostgreSQL, SQL. Available ASAP.",
];

const experiencesRu: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Fullstack / Frontend-разработчик",
    period: "09.2025 – н.в.",
    location: "Удалённо",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "React-продукт для стримеров: Mini App, кабинет, OBS overlay",
        problem:
          "Стример принимает донаты в Telegram и показывает алерты в OBS: три клиента должны работать с одним backend без рассинхрона.",
        contribution:
          "Реализовал три клиента на React + Vite + TypeScript: кабинет, Telegram Mini App, OBS overlay. REST через Orval/OpenAPI, real-time на WebSocket. Backend-интеграция с Django REST. GitHub Actions: lint, build, deploy.",
        stack: ["React", "TypeScript", "Vite", "REST API", "Orval", "WebSocket", "Django REST", "Git"],
        outcomes: [
          "Сценарий доната от Mini App до алерта в эфире",
          "Orval синхронизирует типы с OpenAPI-контрактом backend",
          "CI/CD выкатывает три клиента из одного репозитория",
        ],
      },
      {
        title: "POTALONU / PREEGLOS",
        tagline: "Интернет-витрина билетов и редактор схем залов",
        problem:
          "Билетному сервису нужны витрина с checkout, Telegram Mini App и embed-виджет выбора мест для партнёров.",
        contribution:
          "Собрал витрину на Next.js 16: PostgreSQL, Drizzle ORM, Auth.js, SQL-схема данных. Редактор залов на Canvas/SVG, REST через Orval. GitLab CI/CD, Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "SQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Покупка билета в вебе и Mini App на общей бизнес-логике",
          "Партнёры встраивают виджет выбора мест без форка кода",
          "Деплой через Docker Compose и GitLab pipeline",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Frontend-разработчик",
    period: "04.2024 – 07.2025",
    location: "Удалённо",
    blocks: [
      {
        title: "НКЗ 3.0 — согласование закупок",
        tagline: "Enterprise React-модуль: RBAC, статусы, длинные формы",
        problem:
          "Внутренний сервис закупок требовал единого UI для ролей, статусов и многошагового согласования заявок.",
        contribution:
          "Собрал UI модуля на React + TypeScript: Keycloak SSO, Orval по OpenAPI, react-hook-form, внутренние npm-пакеты UI Kit. Vite code splitting. Scrum, code review в команде.",
        stack: ["React", "TypeScript", "JavaScript", "Vite", "REST API", "Orval", "Git", "Scrum"],
        outcomes: [
          "RBAC и статусы покрывают полный цикл согласования закупок",
          "Orval убрал ручную синхронизацию типов при смене API",
          "Code splitting ускорил загрузку длинных сценариев согласования",
        ],
      },
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend-разработчик",
    period: "06.2023 – 03.2024",
    location: "Удалённо",
    blocks: [
      {
        title: "Thread Intelligence",
        tagline: "React + GraphQL: аналитика связей для SOC",
        problem:
          "Аналитикам нужны граф связей, фильтры и отчёты в одном интерфейсе без переключения между инструментами.",
        contribution:
          "Развивал страницу анализа на React + TypeScript: GraphQL (Apollo Client), MobX, React Query, Orval. Граф на D3.js, виртуализация списков, дашборды. Jest, code review.",
        stack: ["React", "TypeScript", "GraphQL", "REST API", "D3.js", "Jest", "Git"],
        outcomes: [
          "Аналитики строят цепочки связей между сущностями в одном экране",
          "Отчёты подключены к той же GraphQL-модели, что и основные сценарии",
          "Виртуализация держит большие таблицы без просадки UX",
        ],
      },
    ],
  },
  {
    company: "НЛМК",
    role: "Frontend-разработчик",
    period: "05.2022 – 06.2023",
    location: "Удалённо",
    blocks: [
      {
        title: "Регистрация выпусков чугуна",
        tagline: "React SPA вместо Excel для производственных данных",
        problem:
          "Цех фиксировал выпуски в Excel и разрозненных формах: данные терялись, фильтрация по сменам занимала время.",
        contribution:
          "Собрал SPA на React + TypeScript: TanStack Table + React Query, Keycloak SSO, RBAC. GitLab CI на merge request, Sentry в production. Code review.",
        stack: ["React", "TypeScript", "TanStack Table", "REST API", "Keycloak", "GitLab CI", "Sentry"],
        outcomes: [
          "Ключевые операции цеха переведены в web-интерфейс",
          "Таблицы с фильтрами работают на больших объёмах данных",
          "Sentry сократил время диагностики ошибок на production",
        ],
      },
    ],
  },
  {
    company: "Citilink",
    role: "Frontend-разработчик",
    period: "04.2021 – 04.2022",
    location: "Удалённо",
    blocks: [
      {
        title: "citilink.ru — каталог интернет-магазина",
        tagline: "Миграция e-commerce с PHP/Symfony на Next.js + React",
        problem:
          "Крупный интернет-магазин переносил каталог и главную с PHP/Symfony на Next.js: нужны фильтры, SEO и REST без регрессий.",
        contribution:
          "Разрабатывал каталог на React + Next.js: фильтрация, сортировка, пагинация, состояние в URL. REST API с backend и микросервисами. Монорепо yarn workspaces, Redux, Jest. Code review.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "REST API", "Redux", "Jest", "Git"],
        outcomes: [
          "Каталог и главная работают на Next.js с сохранением SEO",
          "Фильтры синхронизированы с URL для оптовых и розничных сценариев",
          "Shared npm-пакеты переиспользуются между страницами монорепо",
        ],
      },
    ],
  },
];

const experiencesEn: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Fullstack / Frontend engineer",
    period: "Sep 2025 – present",
    location: "Remote",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "React product for streamers: Mini App, dashboard, OBS overlay",
        problem:
          "Streamers accept tips in Telegram and show OBS alerts: three clients must stay in sync with one backend.",
        contribution:
          "Built three React + Vite + TypeScript clients: dashboard, Telegram Mini App, OBS overlay. REST via Orval/OpenAPI, real-time WebSocket. Django REST backend integration. GitHub Actions CI/CD.",
        stack: ["React", "TypeScript", "Vite", "REST API", "Orval", "WebSocket", "Django REST", "Git"],
        outcomes: [
          "End-to-end donation flow from Mini App to on-stream alert",
          "Orval keeps types aligned with OpenAPI backend contracts",
          "CI/CD ships all three clients from one repository",
        ],
      },
      {
        title: "POTALONU / PREEGLOS",
        tagline: "Ticket storefront and hall layout editor",
        problem:
          "The ticketing service needed a checkout storefront, Telegram Mini App, and embeddable seat picker for partners.",
        contribution:
          "Built Next.js 16 storefront: PostgreSQL, Drizzle ORM, Auth.js, SQL data model. Canvas/SVG hall editor, Orval REST client. GitLab CI/CD, Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "SQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Ticket purchase works in web and Mini App on shared logic",
          "Partners embed seat picker without forking code",
          "Deploy via Docker Compose and GitLab pipeline",
        ],
      },
    ],
  },
  {
    company: "X5 Tech",
    role: "Frontend engineer",
    period: "Apr 2024 – Jul 2025",
    location: "Remote",
    blocks: [
      {
        title: "NKZ 3.0 — procurement approval",
        tagline: "Enterprise React module: RBAC, statuses, long forms",
        problem:
          "Internal procurement needed one UI for roles, statuses, and multi-step approval flows.",
        contribution:
          "Built module UI on React + TypeScript: Keycloak SSO, Orval from OpenAPI, react-hook-form, internal npm UI Kit. Vite code splitting. Scrum, code review.",
        stack: ["React", "TypeScript", "JavaScript", "Vite", "REST API", "Orval", "Git", "Scrum"],
        outcomes: [
          "RBAC and statuses cover the full procurement cycle",
          "Orval removed manual type sync when API changed",
          "Code splitting improved load time on long approval flows",
        ],
      },
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend engineer",
    period: "Jun 2023 – Mar 2024",
    location: "Remote",
    blocks: [
      {
        title: "Thread Intelligence",
        tagline: "React + GraphQL analytics for SOC",
        problem:
          "Analysts needed relationship graphs, filters, and reports on one screen without switching tools.",
        contribution:
          "Extended analysis page on React + TypeScript: GraphQL (Apollo Client), MobX, React Query, Orval. D3.js graph, virtualized lists, dashboards. Jest, code review.",
        stack: ["React", "TypeScript", "GraphQL", "REST API", "D3.js", "Jest", "Git"],
        outcomes: [
          "Analysts build entity chains on one screen",
          "Reports wired to the same GraphQL model as core flows",
          "Virtualization keeps large tables responsive",
        ],
      },
    ],
  },
  {
    company: "NLMK",
    role: "Frontend engineer",
    period: "May 2022 – Jun 2023",
    location: "Remote",
    blocks: [
      {
        title: "Cast iron release registration",
        tagline: "React SPA replacing Excel for production data",
        problem:
          "The shop floor tracked releases in Excel: data was lost and shift filtering was slow.",
        contribution:
          "Built React + TypeScript SPA: TanStack Table + React Query, Keycloak SSO, RBAC. GitLab CI on MR, Sentry in production. Code review.",
        stack: ["React", "TypeScript", "TanStack Table", "REST API", "Keycloak", "GitLab CI", "Sentry"],
        outcomes: [
          "Core shop-floor operations moved to a web interface",
          "Filtered tables handle large datasets in production",
          "Sentry reduced production incident diagnosis time",
        ],
      },
    ],
  },
  {
    company: "Citilink",
    role: "Frontend engineer",
    period: "Apr 2021 – Apr 2022",
    location: "Remote",
    blocks: [
      {
        title: "citilink.ru — online store catalog",
        tagline: "E-commerce migration from PHP/Symfony to Next.js + React",
        problem:
          "A major online store migrated catalog and homepage from PHP/Symfony to Next.js with filters, SEO, and REST intact.",
        contribution:
          "Built catalog on React + Next.js: filters, sort, pagination, URL state. REST API with backend and microservices. Yarn workspaces monorepo, Redux, Jest. Code review.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "REST API", "Redux", "Jest", "Git"],
        outcomes: [
          "Catalog and homepage on Next.js with SEO preserved",
          "URL-synced filters for wholesale and retail flows",
          "Shared npm packages reused across monorepo pages",
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
