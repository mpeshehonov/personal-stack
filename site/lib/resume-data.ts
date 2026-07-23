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
  "Senior Frontend Engineer, 7 лет. Стек: React, TypeScript, JavaScript, Next.js, REST API, CI/CD.",
  "Делаю сложные интерфейсы и довожу до production: роли и доступы, длинные формы, GraphQL, WebSocket, CI/CD, разбор ошибок в проде.",
  "Работал в X5, BI.ZONE, НЛМК, Citilink. В POTALONU был единственным frontend: донаты для стримеров и редактор схем залов на Canvas. Ищу remote Senior Frontend с ответственностью за модуль от API до релиза.",
];

const aboutParagraphsEn = [
  "Senior Frontend Engineer, 7 years. Stack: React, TypeScript, JavaScript, Next.js, REST API, CI/CD.",
  "I build complex UIs and ship them to production: roles and access, long forms, GraphQL, WebSocket, CI/CD, production debugging.",
  "Worked at X5, BI.ZONE, NLMK, Citilink. At POTALONU I was the sole frontend: streamer donations and a Canvas hall-layout editor. Looking for a remote Senior Frontend role with ownership of a module from API to release.",
];

const experiencesRu: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Senior Frontend Engineer",
    period: "09.2025 - 06.2026",
    location: "Удалённо",
    companyBlurb: "Билеты и инструменты для стримеров",
    companyUrl: "https://potalonu.com",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Единственный frontend: мини-приложение, кабинет, оверлей",
        problem: "Нужны мини-приложение для донатов, кабинет стримера и оверлей на одном backend без рассинхрона.",
        contribution:
          "Единственный frontend: React, Vite, TypeScript; REST API, WebSocket-алерты, GitHub Actions, Sentry.",
        stack: ["React", "TypeScript", "JavaScript", "Vite", "WebSocket", "CI/CD", "GitHub Actions", "Sentry"],
        outcomes: [
          "Собрал на React мини-приложение для донатов, кабинет стримера и оверлей с алертами и прогрессбаром; довёл до production",
          "Подключил REST API и live-алерты по WebSocket",
          "Настроил CI/CD (GitHub Actions) и Sentry: три клиента на одном API без рассинхрона с backend",
          "Закрыл полный сценарий: оплата в Mini App, кабинет стримера, алерт на эфире в OBS",
        ],
      },
      {
        title: "PREEGLOS",
        tagline: "Витрина билетов и редактор схем залов",
        problem: "Нужны checkout и свой редактор схем залов вместо seats.io.",
        contribution:
          "Next.js-витрина (Auth.js, PostgreSQL, Orval) плюс редактор залов на Canvas и встраиваемый виджет выбора мест; CI/CD (GitLab CI), Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "Canvas", "PostgreSQL", "CI/CD", "GitLab CI"],
        outcomes: [
          "Собрал витрину и checkout на Next.js: Auth.js, PostgreSQL, REST API по OpenAPI",
          "Сделал редактор схем залов на Canvas и встраиваемый виджет выбора мест вместо seats.io",
          "В production: десятки залов и событий - организаторы рисуют схему сами, покупатели выбирают места на сайте",
          "Настроил CI/CD (GitLab CI) и выкладку через Docker Compose",
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
        stack: ["React", "TypeScript", "JavaScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "Один из 2 frontend: React, TypeScript, роли (Keycloak), длинные формы, REST API (Orval), UI Kit",
          "Сам перевёл модуль на Vite с разделением кода (code splitting) на длинных сценариях",
          "Закрыл UI полного цикла согласования: роли, статусы, формы, переходы этапов",
          "Вёл code review и декомпозицию frontend-модулей вместе с backend",
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
        stack: ["React", "TypeScript", "JavaScript", "GraphQL", "Apollo", "D3.js", "Jest"],
        outcomes: [
          "Собрал разделы категорий угроз и детальную форму связей на GraphQL (Apollo)",
          "Добавил виртуализацию длинных списков; покрыл тестами (Jest); вёл code review",
          "Категории и форма стали основным способом связывать угрозы в продукте",
          "Собрал часть графа связей сущностей на D3.js для аналитиков",
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
          "React SPA: TanStack Table, React Query, Keycloak; CI/CD (GitLab CI), Sentry. Командировка на цех.",
        stack: ["React", "TypeScript", "JavaScript", "TanStack Table", "TanStack Query", "Keycloak", "CI/CD", "Sentry"],
        outcomes: [
          "Заменил Excel на React SPA: таблицы (TanStack Table), React Query, Keycloak",
          "Съездил на цех, посмотрел реальный сценарий смены и учёл его в интерфейсе",
          "Цех перешёл на web как основной процесс (десятки пользователей на сменах)",
          "Подключил Sentry и CI/CD (GitLab CI): быстрее находил и чинил ошибки в проде",
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
        title: "Каталог",
        tagline: "Миграция с PHP/Symfony на Next.js",
        problem: "Перенос каталога на Next.js с фильтрами, SEO и REST к микросервисам.",
        contribution:
          "Зона каталога: фильтры, сортировка, пагинация, состояние в URL, REST API; code review в yarn workspaces.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "REST API", "Redux", "Jest"],
        outcomes: [
          "Перенёс зону каталога на Next.js: фильтры, сортировка, пагинация, REST API, состояние в URL",
          "Сохранил SEO: страницы и фильтры индексируются через URL",
          "Одно состояние фильтров в URL работает для розницы и оптового каталога",
          "Вёл code review в монорепозитории (yarn workspaces)",
        ],
      },
    ],
  },
];

const experiencesEn: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Senior Frontend Engineer",
    period: "Sep 2025 - Jun 2026",
    location: "Remote",
    companyBlurb: "Ticketing and streamer tools",
    companyUrl: "https://potalonu.com",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "Sole frontend: Mini App, streamer dashboard, overlay",
        problem: "Needed a donation Mini App, streamer dashboard, and overlay on one backend without drift.",
        contribution:
          "Sole frontend: React, Vite, TypeScript; REST API, WebSocket alerts, GitHub Actions, Sentry.",
        stack: ["React", "TypeScript", "JavaScript", "Vite", "WebSocket", "CI/CD", "GitHub Actions", "Sentry"],
        outcomes: [
          "Built on React a donation Mini App, streamer dashboard, and overlay with alerts and progress bar; shipped to production",
          "Connected REST API and live WebSocket alerts",
          "Set up CI/CD (GitHub Actions) and Sentry: three clients on one API without FE/backend drift",
          "Closed the full path: pay in Mini App, streamer dashboard, live alert in OBS",
        ],
      },
      {
        title: "PREEGLOS",
        tagline: "Ticket storefront and hall layout editor",
        problem: "Needed checkout and an in-house hall editor instead of seats.io.",
        contribution:
          "Next.js storefront (Auth.js, PostgreSQL, Orval) plus Canvas hall editor and embeddable seat picker; CI/CD (GitLab CI), Docker Compose.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "Canvas", "PostgreSQL", "CI/CD", "GitLab CI"],
        outcomes: [
          "Built the storefront and checkout on Next.js: Auth.js, PostgreSQL, REST API from OpenAPI",
          "Built a Canvas hall-layout editor and an embeddable seat-picker widget instead of seats.io",
          "In production: dozens of halls and events - organizers draw layouts themselves, buyers pick seats on the site",
          "Set up CI/CD (GitLab CI) and delivery with Docker Compose",
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
        stack: ["React", "TypeScript", "JavaScript", "Vite", "Orval", "Keycloak", "react-hook-form"],
        outcomes: [
          "One of 2 frontend engineers: React, TypeScript, Keycloak roles, long forms, REST API (Orval), UI Kit",
          "Owned the Vite migration with code splitting on long flows",
          "Covered the full approval UI cycle: roles, statuses, forms, stage transitions",
          "Ran code review and breakdown of frontend modules with backend",
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
        stack: ["React", "TypeScript", "JavaScript", "GraphQL", "Apollo", "D3.js", "Jest"],
        outcomes: [
          "Built threat-category sections and a detail form for relationships on GraphQL (Apollo)",
          "Added list virtualization; covered with tests (Jest); ran code review",
          "Categories and the detail form became the main way to link threats in the product",
          "Built part of the entity relationship graph on D3.js for analysts",
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
          "React SPA: TanStack Table, React Query, Keycloak; CI/CD (GitLab CI), Sentry. Plant visit under the real shift scenario.",
        stack: ["React", "TypeScript", "JavaScript", "TanStack Table", "TanStack Query", "Keycloak", "CI/CD", "Sentry"],
        outcomes: [
          "Replaced Excel with a React SPA: tables (TanStack Table), React Query, Keycloak",
          "Visited the plant, watched the real shift flow, and reflected it in the UI",
          "Plant teams moved to web as the primary process (dozens of shift users)",
          "Wired Sentry and CI/CD (GitLab CI): faster to find and fix production errors",
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
        title: "Catalog",
        tagline: "Migration from PHP/Symfony to Next.js",
        problem: "Move catalog to Next.js with filters, SEO, and microservice REST.",
        contribution:
          "Catalog scope: filters, sort, pagination, URL state, REST API; code review in yarn workspaces.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "REST API", "Redux", "Jest"],
        outcomes: [
          "Moved the catalog zone to Next.js: filters, sort, pagination, REST API, URL state",
          "Kept SEO: pages and filters stay indexable via the URL",
          "One URL filter state works for both retail and wholesale catalog views",
          "Ran code review in a monorepo (yarn workspaces)",
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
