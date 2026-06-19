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
  "Senior Frontend-разработчик, 7+ лет: React, TypeScript, Next.js для e-commerce, enterprise-модулей и продуктовых интерфейсов. Проектирую сложные UI, связываю frontend с typed API-контрактами и довожу фичи до production через review и CI/CD.",
  "Другие задачи и кейсы — в разделе Проекты на сайте. Backend-интеграция: Django REST, Nest.js, PostgreSQL, SQL. Сочи, удалённо. Готов к выходу ASAP.",
];

const aboutParagraphsEn = [
  "Senior Frontend engineer with 7+ years building React, TypeScript, and Next.js interfaces for e-commerce, enterprise modules, and product workflows. Strong in complex UI, typed API contracts, production delivery, and code review.",
  "Other work and case studies — in the Projects section on the site. Backend integration: Django REST, Nest.js, PostgreSQL, SQL. Sochi, remote. Available ASAP.",
];

const experiencesRu: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Frontend-разработчик",
    period: "09.2025 – н.в.",
    location: "Удалённо",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "React-продукт для стримеров: Mini App, кабинет, OBS overlay",
        problem:
          "Стример принимает донаты в Telegram и показывает алерты в OBS: три клиента должны работать с одним backend без рассинхрона.",
        contribution:
          "Спроектировал и реализовал frontend-контур sendonate.com из трёх React + Vite + TypeScript клиентов: кабинет стримера, Telegram Mini App и OBS overlay. Завёл типизированный REST-клиент через Orval/OpenAPI, real-time доставку событий по WebSocket и CI/CD в GitHub Actions для lint/build/deploy всех клиентов из одного репозитория.",
        stack: ["React", "TypeScript", "Vite", "REST API", "Orval", "WebSocket", "Django REST", "GitHub Actions"],
        outcomes: [
          "End-to-end сценарий доната до production: Mini App → backend → alert в OBS overlay без ручного обновления эфира",
          "Orval генерирует DTO и методы API из OpenAPI-контракта — рассинхрон frontend/backend ловится на сборке",
          "Единый delivery pipeline для трёх клиентов: автоматические проверки, сборка и деплой без ручных операций",
        ],
      },
      {
        title: "POTALONU / PREEGLOS",
        tagline: "Интернет-витрина билетов и редактор схем залов",
        problem:
          "Билетному сервису нужны витрина с checkout, Telegram Mini App и embed-виджет выбора мест для партнёров.",
        contribution:
          "Реализовал web-витрину PREEGLOS на Next.js с checkout-сценарием, Auth.js, PostgreSQL/Drizzle и типизированным REST-клиентом через Orval. Отдельно собрал редактор схем залов на Canvas/SVG и embeddable seat picker для партнёрских сайтов; настроил GitLab CI/CD и Docker Compose delivery.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "SQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Покупка билета в вебе и Telegram Mini App на общей модели данных и API-контрактах",
          "Партнёры подключают seat picker без форка продукта: схема зала и выбор мест в одном frontend-контуре",
          "Production delivery: Docker Compose окружение и GitLab pipeline собирают и выкатывают сервис без ручной сборки",
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
          "Разрабатывал enterprise-модуль согласования закупок на React + TypeScript: ролевой доступ через Keycloak SSO, многошаговые формы на react-hook-form, типизированный API-слой через Orval/OpenAPI и компоненты из внутреннего npm UI Kit. Участвовал в code review и выносил тяжёлые сценарии в отдельные chunks через Vite code splitting.",
        stack: ["React", "TypeScript", "JavaScript", "Vite", "REST API", "Orval", "Keycloak", "Git"],
        outcomes: [
          "Frontend закрывает полный цикл закупочного согласования: роли, статусы, формы и переходы между этапами",
          "OpenAPI/Orval сделал API-контракты проверяемыми на сборке вместо ручного обновления типов",
          "Vite code splitting разделил тяжёлые approval-сценарии на независимые чанки и снизил риск регрессий",
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
        title: "Threat Intelligence",
        tagline: "React + GraphQL: аналитика связей для SOC",
        problem:
          "Аналитикам нужны граф связей, фильтры и отчёты в одном интерфейсе без переключения между инструментами.",
        contribution:
          "Развивал аналитический интерфейс для SOC на React + TypeScript: GraphQL/Apollo для основной модели данных, MobX/React Query для состояния и запросов, D3.js для графа связей, виртуализация для больших списков и Jest для регрессионных проверок. Участвовал в code review и доработке UX сложных аналитических сценариев.",
        stack: ["React", "TypeScript", "GraphQL", "REST API", "D3.js", "Jest", "Git"],
        outcomes: [
          "Граф связей, фильтры и отчёты объединены в одном рабочем экране аналитика",
          "Единый GraphQL data layer для аналитики и отчётов — меньше расхождений между экраном и выгрузками",
          "Виртуализация сохраняет отзывчивость интерфейса на больших списках сущностей",
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
          "Разработал production SPA для регистрации выпусков чугуна на React + TypeScript: таблицы и фильтры на TanStack Table, серверное состояние через React Query, Keycloak SSO/RBAC для доступа по ролям. Подключил GitLab CI checks на merge request и Sentry для диагностики production-ошибок.",
        stack: ["React", "TypeScript", "TanStack Table", "TanStack Query", "REST API", "Keycloak", "GitLab CI", "Sentry"],
        outcomes: [
          "Ключевые операции смены переведены из Excel в web-интерфейс с авторизацией и ролевыми правами",
          "Таблицы и фильтры пригодны для производственных объёмов данных",
          "Sentry даёт production visibility: ошибки привязаны к релизам и стек-трейсам без воспроизведения на рабочем месте",
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
          "Участвовал в миграции e-commerce каталога и главной citilink.ru с PHP/Symfony на React + Next.js: фильтрация, сортировка, пагинация и URL-состояние для SEO и шаринга. Интегрировал REST API backend/микросервисов, работал в yarn workspaces монорепо, покрывал критичную логику Jest-тестами и проходил code review.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "REST API", "Redux", "Jest", "Git"],
        outcomes: [
          "SEO-контур каталога сохранён при миграции на Next.js: индексируемые страницы и URL-состояние фильтров",
          "Retail/wholesale сценарии через синхронизацию фильтров, сортировки и пагинации с URL",
          "Shared npm-пакеты в yarn workspaces снизили дублирование между страницами каталога",
        ],
      },
    ],
  },
];

const experiencesEn: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Frontend engineer",
    period: "Sep 2025 – present",
    location: "Remote",
    blocks: [
      {
        title: "sendonate.com",
        tagline: "React product for streamers: Mini App, dashboard, OBS overlay",
        problem:
          "Streamers accept tips in Telegram and show OBS alerts: three clients must stay in sync with one backend.",
        contribution:
          "Designed and built the sendonate.com frontend: three React + Vite + TypeScript clients — streamer dashboard, Telegram Mini App, and OBS overlay. Typed REST client via Orval/OpenAPI, real-time event delivery over WebSocket, and GitHub Actions CI/CD for lint/build/deploy of all clients from one repository.",
        stack: ["React", "TypeScript", "Vite", "REST API", "Orval", "WebSocket", "Django REST", "GitHub Actions"],
        outcomes: [
          "End-to-end donation flow in production: Mini App → backend → OBS overlay alert without manual stream refresh",
          "Orval generates DTOs and API methods from OpenAPI contracts — frontend/backend drift caught at build time",
          "Unified delivery pipeline for three clients: automated checks, build, and deploy without manual release steps",
        ],
      },
      {
        title: "POTALONU / PREEGLOS",
        tagline: "Ticket storefront and hall layout editor",
        problem:
          "The ticketing service needed a checkout storefront, Telegram Mini App, and embeddable seat picker for partners.",
        contribution:
          "Built PREEGLOS web storefront on Next.js with checkout, Auth.js, PostgreSQL/Drizzle, and typed REST client via Orval. Canvas/SVG hall layout editor and embeddable seat picker for partner sites; GitLab CI/CD and Docker Compose delivery.",
        stack: ["Next.js", "React", "TypeScript", "PostgreSQL", "SQL", "Orval", "Docker", "GitLab CI"],
        outcomes: [
          "Ticket purchase in web and Telegram Mini App on shared data model and API contracts",
          "Partners embed seat picker without forking: hall layout and seat selection in one frontend surface",
          "Production delivery: Docker Compose environment and GitLab pipeline build and deploy without manual server builds",
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
          "Developed enterprise procurement approval module on React + TypeScript: role-based access via Keycloak SSO, multi-step forms with react-hook-form, typed API layer via Orval/OpenAPI, and internal npm UI Kit components. Participated in code review and split heavy flows into separate chunks via Vite code splitting.",
        stack: ["React", "TypeScript", "JavaScript", "Vite", "REST API", "Orval", "Keycloak", "Git"],
        outcomes: [
          "Frontend covers the full procurement cycle: roles, statuses, forms, and stage transitions",
          "OpenAPI/Orval made API contracts verifiable at build time instead of manual type updates",
          "Vite code splitting split heavy approval flows into independent chunks and reduced regression risk",
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
        title: "Threat Intelligence",
        tagline: "React + GraphQL analytics for SOC",
        problem:
          "Analysts needed relationship graphs, filters, and reports on one screen without switching tools.",
        contribution:
          "Extended SOC analytics interface on React + TypeScript: GraphQL/Apollo for core data model, MobX/React Query for state and queries, D3.js relationship graph, list virtualization, and Jest regression checks. Participated in code review and UX improvements for complex analytical flows.",
        stack: ["React", "TypeScript", "GraphQL", "REST API", "D3.js", "Jest", "Git"],
        outcomes: [
          "Relationship graph, filters, and reports unified on one analyst workspace",
          "Single GraphQL data layer for analytics and reports — fewer mismatches between screen and exports",
          "Virtualization keeps the interface responsive on large entity lists",
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
          "Built production SPA for cast iron release registration on React + TypeScript: TanStack Table filters, React Query server state, Keycloak SSO/RBAC for role-based access. GitLab CI checks on merge requests and Sentry for production error diagnosis.",
        stack: ["React", "TypeScript", "TanStack Table", "TanStack Query", "REST API", "Keycloak", "GitLab CI", "Sentry"],
        outcomes: [
          "Core shift operations moved from Excel to a web interface with auth and role-based permissions",
          "Tables and filters handle production-scale data volumes",
          "Sentry provides production visibility: errors tied to releases and stack traces without on-site reproduction",
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
          "Contributed to citilink.ru e-commerce catalog and homepage migration from PHP/Symfony to React + Next.js: filters, sort, pagination, and URL state for SEO and sharing. Integrated REST API with backend and microservices, worked in yarn workspaces monorepo, covered critical logic with Jest tests, and participated in code review.",
        stack: ["Next.js", "React", "TypeScript", "JavaScript", "REST API", "Redux", "Jest", "Git"],
        outcomes: [
          "Catalog SEO preserved on Next.js migration: indexable pages and URL-synced filter state",
          "Retail/wholesale flows via URL-synced filters, sort, and pagination",
          "Shared npm packages in yarn workspaces reduced duplication across catalog pages",
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
