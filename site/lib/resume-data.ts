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
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Донаты для стримеров: Mini App, OBS overlay, кабинет",
        problem:
          "Стримеру нужен приём донатов в Telegram и live-алерт в OBS без ручной интеграции с backend.",
        contribution:
          "Три клиента на React + Vite: кабинет стримера, Telegram Mini App, OBS overlay. REST через Orval, overlay на WebSocket. GitHub Actions для lint, build и деплоя.",
        stack: ["React", "Vite", "TypeScript", "Telegram Mini App", "Orval", "WebSocket", "GitHub Actions"],
        outcomes: [
          "Mini App принимает оплату донатов и синхронизируется с backend",
          "OBS overlay показывает алерты в эфире без задержки UI",
          "CI/CD выкатывает все три клиента из одного репозитория",
        ],
      },
      {
        title: "POTALONU / PREEGLOS",
        tagline: "Билетная витрина и редактор схем залов",
        problem:
          "Организаторам нужна витрина событий с checkout и интерактивный выбор мест для сайтов партнёров.",
        contribution:
          "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js. Редактор схем залов на Canvas/SVG и embed-виджет выбора мест. GitLab CI/CD, Docker Compose, REST через Orval.",
        stack: ["Next.js", "PostgreSQL", "Drizzle ORM", "Auth.js", "Canvas", "Docker", "GitLab CI", "Orval"],
        outcomes: [
          "Checkout и Telegram Mini App работают в одном продуктовом контуре",
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
        tagline: "Enterprise-модуль с RBAC и длинными цепочками статусов",
        problem:
          "Закупки X5 требуют согласования по ролям и статусам в одном UI с десятками шагов на заявку.",
        contribution:
          "Собрал UI модуля: Keycloak SSO, Orval по OpenAPI, формы на react-hook-form, внутренние npm-пакеты UI Kit. Vite code splitting на длинных сценариях.",
        stack: ["React", "TypeScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "RBAC и статусы покрывают полный цикл согласования закупок",
          "Code splitting держит UX на длинных формах без просадки загрузки",
          "Scrum, code review, работа с внутренним UI Kit",
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
        tagline: "Анализ связей между сущностями для SOC",
        problem:
          "Аналитикам безопасности нужен граф связей, фильтры и отчёты в одном экране без переключения между инструментами.",
        contribution:
          "Страница анализа: GraphQL на Apollo Client, MobX, React Query, Orval; граф связей на D3.js; виртуализация списков; дашборды Highcharts/Recharts; npm-пакеты @bizone; Jest.",
        stack: ["React", "GraphQL", "Apollo Client", "D3.js", "MobX", "React Query", "Orval", "Highcharts"],
        outcomes: [
          "Аналитики строят цепочки связей между сущностями в одном экране",
          "Динамические отчёты подключены к той же GraphQL-модели",
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
        tagline: "Web-приложение вместо Excel и разрозненных форм",
        problem:
          "Цех фиксировал выпуски чугуна в Excel и разрозненных формах, данные терялись и дублировались.",
        contribution:
          "Собрал SPA на React: TanStack Table + React Query на больших объёмах, Keycloak SSO и RBAC, внутренние npm-пакеты shared UI. GitLab CI на MR, Sentry в production.",
        stack: ["React", "TanStack Table", "TanStack Query", "Keycloak", "GitLab CI", "Sentry"],
        outcomes: [
          "Единый интерфейс регистрации выпусков вместо таблиц Excel",
          "Таблицы с большими объёмами данных без просадки производительности",
          "Ошибки отслеживаются в Sentry на production",
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
        title: "Миграция каталога на Next.js",
        tagline: "E-commerce каталог и главная с PHP/Symfony на React",
        problem:
          "Каталог и главная работали на PHP/Symfony; нужна миграция на Next.js без потери SEO и фильтров.",
        contribution:
          "Перенёс каталог и главную в монорепозиторий yarn workspaces со shared npm-пакетами. Фильтры, сортировка, пагинация, состояние в URL. REST API с backend и микросервисами, Redux, Jest.",
        stack: ["Next.js", "React", "Redux", "yarn workspaces", "REST API", "Jest"],
        outcomes: [
          "Каталог и главная на Next.js с сохранением SEO и фильтров",
          "Shared npm-пакеты переиспользуются между страницами монорепо",
          "Code review и Jest на критичные сценарии каталога",
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
        tagline: "Streamer donations: Mini App, OBS overlay, dashboard",
        problem:
          "Streamers needed Telegram donations and live OBS alerts without manual backend integration.",
        contribution:
          "Three React + Vite clients: streamer dashboard, Telegram Mini App, OBS overlay. Orval REST client, WebSocket overlay. GitHub Actions for lint, build, and deploy.",
        stack: ["React", "Vite", "TypeScript", "Telegram Mini App", "Orval", "WebSocket", "GitHub Actions"],
        outcomes: [
          "Mini App handles donation checkout synced with backend",
          "OBS overlay shows live alerts without UI lag",
          "CI/CD ships all three clients from one repo",
        ],
      },
      {
        title: "POTALONU / PREEGLOS",
        tagline: "Event storefront and hall layout editor",
        problem:
          "Organizers needed an event storefront with checkout and interactive seat selection for partner sites.",
        contribution:
          "Next.js 16, PostgreSQL, Drizzle ORM, Auth.js. Hall layout editor on Canvas/SVG and embeddable seat picker. GitLab CI/CD, Docker Compose, Orval REST client.",
        stack: ["Next.js", "PostgreSQL", "Drizzle ORM", "Auth.js", "Canvas", "Docker", "GitLab CI", "Orval"],
        outcomes: [
          "Checkout and Telegram Mini App in one product stack",
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
        tagline: "Enterprise module with RBAC and long status chains",
        problem:
          "X5 procurement required role-based approval and status tracking in one UI with dozens of steps per request.",
        contribution:
          "Built module UI: Keycloak SSO, Orval from OpenAPI, react-hook-form, internal npm UI Kit packages. Vite code splitting on long approval flows.",
        stack: ["React", "TypeScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "RBAC and statuses cover the full procurement approval cycle",
          "Code splitting keeps UX on long forms without load regressions",
          "Scrum, code review, internal UI Kit integration",
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
        tagline: "Entity relationship analysis for SOC",
        problem:
          "Security analysts needed relationship graphs, filters, and reports on one screen without switching tools.",
        contribution:
          "Entity analysis page: GraphQL on Apollo Client, MobX, React Query, Orval; relationship graph on D3.js; virtualized lists; Highcharts/Recharts dashboards; @bizone npm packages; Jest.",
        stack: ["React", "GraphQL", "Apollo Client", "D3.js", "MobX", "React Query", "Orval", "Highcharts"],
        outcomes: [
          "Analysts build entity relationship chains on one screen",
          "Dynamic reports wired to the same GraphQL model",
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
        tagline: "Web app replacing Excel and scattered forms",
        problem:
          "The shop floor tracked cast iron releases in Excel and scattered forms; data was lost and duplicated.",
        contribution:
          "Built React SPA: TanStack Table + React Query on large datasets, Keycloak SSO and RBAC, internal shared UI npm packages. GitLab CI on MR, Sentry in production.",
        stack: ["React", "TanStack Table", "TanStack Query", "Keycloak", "GitLab CI", "Sentry"],
        outcomes: [
          "Single registration UI replaced Excel spreadsheets",
          "Tables with large datasets stay performant",
          "Production errors tracked in Sentry",
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
        title: "Catalog migration to Next.js",
        tagline: "E-commerce catalog and homepage from PHP/Symfony to React",
        problem:
          "Catalog and homepage ran on PHP/Symfony; migration to Next.js was required without losing SEO and filters.",
        contribution:
          "Migrated catalog and homepage into yarn workspaces monorepo with shared npm packages. Filters, sort, pagination, URL state. REST API with backend and microservices, Redux, Jest.",
        stack: ["Next.js", "React", "Redux", "yarn workspaces", "REST API", "Jest"],
        outcomes: [
          "Catalog and homepage on Next.js with SEO and filters preserved",
          "Shared npm packages reused across monorepo pages",
          "Code review and Jest on critical catalog flows",
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
