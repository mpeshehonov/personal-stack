export type Experience = {
  company: string;
  role: string;
  period: string;
  location: string;
  projects?: { name: string; stack: string; bullets: string[] }[];
  bullets?: string[];
};

export const aboutText = `Senior Frontend / Fullstack разработчик. Занимаюсь веб-разработкой с 2018 года: B2B, e-commerce, маркетплейсы, real-time и Telegram Mini Apps. Проектирую и довожу до продакшена сценарии с большим числом состояний, role-based access, typed API contracts и интеграциями с REST, GraphQL и WebSocket.`;

export const experiences: Experience[] = [
  {
    company: "POTALONU LLC",
    role: "Fullstack / Frontend-разработчик",
    period: "09.2025 – н.в.",
    location: "Удалённо",
    projects: [
      {
        name: "sendonate.com",
        stack: "React 19, Vite, TypeScript, Telegram Mini App, REST, OpenAPI/Orval",
        bullets: [
          "Три клиентских контура: веб-кабинет, Telegram Mini App и Vite-бандл для OBS/оверлея",
          "End-to-end сценарий доната с многошаговым флоу оплаты и real-time overlay на WebSocket",
        ],
      },
      {
        name: "POTALONU / PREEGLOS",
        stack: "Next.js 16, React 19, PostgreSQL, Drizzle ORM, Auth.js, Docker, GitLab CI/CD",
        bullets: [
          "Билетный сервис: витрина, покупка билетов, Telegram Mini App",
          "Аналог seats.io: редактор схем залов и embed-виджет выбора мест",
          "Self-hosted поставка: Docker Compose, GitLab CI/CD pipeline",
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
      "Модуль согласования закупочных процедур (НКЗ 3.0): RBAC, статусы, переходы состояний",
      "Orval для генерации типов и API-клиента по OpenAPI",
      "Оптимизация сборки на Vite: code splitting, dynamic imports",
    ],
  },
  {
    company: "BI.ZONE",
    role: "Frontend-разработчик",
    period: "06.2023 – 03.2024",
    location: "Удалённо",
    bullets: [
      "Thread Intelligence: GraphQL, MobX, React Query, графы на Cytoscape.js",
      "Динамические отчёты и дашборды: Highcharts, Recharts, react-grid-layout",
      "Модуль отчётов на GraphQL (Apollo Client)",
    ],
  },
  {
    company: "НЛМК",
    role: "Frontend-разработчик",
    period: "05.2022 – 06.2023",
    location: "Удалённо",
    bullets: [
      "Веб-приложение «Регистрация выпусков чугуна» для доменного производства",
      "Сложные таблицы на TanStack Table с большими объёмами данных",
      "React Query для кэширования, Sentry для мониторинга",
    ],
  },
  {
    company: "Citilink",
    role: "Frontend-разработчик",
    period: "04.2021 – 04.2022",
    location: "Удалённо",
    bullets: [
      "Миграция e-commerce с PHP/Symfony на Next.js: каталог и главная",
      "Фильтрация, сортировка, пагинация, состояние URL через REST API",
      "Согласование API-контрактов между фронтендом и микросервисами",
    ],
  },
];

export const education = [
  {
    school: "Тульский государственный коммунально-строительный техникум",
    field: "Земельно-имущественные отношения",
    period: "2015 – 2018",
    location: "Тула, Россия",
  },
  {
    school: "Компьютерная академия «ШАГ»",
    field: "Веб-разработка",
    period: "2016",
    location: "Тула, Россия",
  },
];

export const achievements =
  "Победитель хакатона «Цифровой прорыв» (2021, 2020), победитель Hack.Genesis _ONLINE_, финалист Virus Hack, эксперт чемпионата WorldSkills.";
