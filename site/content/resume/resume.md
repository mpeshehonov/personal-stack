# Максим Пешехонов

Senior Frontend-разработчик

Сочи, Россия · Email: kassady71@gmail.com · Телефон: +79509196786 · [Telegram: `@makusimu_san`](https://t.me/makusimu_san) · [LinkedIn: `makusimu`](https://www.linkedin.com/in/makusimu) · [GitHub: `mpeshehonov`](https://github.com/mpeshehonov) · Дата рождения: 28.05.1996

## О себе

Senior Frontend / Fullstack разработчик. Занимаюсь веб-разработкой с 2018 года: B2B, e-commerce, маркетплейсы, real-time и Telegram Mini Apps. Делаю интерфейсы со сложными сценариями, RBAC, Orval/OpenAPI и интеграциями REST, GraphQL, WebSocket.

За это время поработал в разных доменах и командах. Кейсы — в разделе «Проекты» на сайте, полный список по запросу.

Основной стек: Next.js, React, TypeScript, Vite, TanStack Query, Orval + OpenAPI, React Hook Form, Zod, Radix UI, Tailwind CSS, Sentry, Playwright. Для fullstack-задач работаю с Nest.js (REST, DTO, Socket.io gateways, TypeORM, PostgreSQL, class-validator) и интеграциями с REST API.

Ключевой опыт: X5 Tech (модуль согласования закупок с ролевой моделью и сложными переходами состояний), НЛМК (внутреннее приложение для производственных данных), BI.ZONE (Thread Intelligence: GraphQL, MobX, React Query, графы и дашборды), Citilink (миграция e-commerce с Symfony на Next.js), коммерческие продукты sendonate.com и POTALONU/PREEGLOS.

## Опыт работы

### POTALONU LLC — Fullstack / Frontend-разработчик

09.2025 – н.в. | Удалённо

sendonate.com — донаты для стримеров (React 19, Vite, TypeScript, Telegram Mini App, REST, OpenAPI/Orval, TanStack Query, React Hook Form, Zod, Sentry)

- Спроектировал и собрал три клиентских контура: веб-кабинет стримера, Telegram Mini App и отдельный Vite-бандл для OBS/оверлея эфира.
- Реализовал полный сценарий доната: многошаговый флоу оплаты в Mini App, REST через Orval-клиент по OpenAPI, кабинет с CRUD коллекций, пагинацией, debounce-поиском и настройками алертов.
- Собрал real-time overlay на WebSocket с reconnect, очередью алертов, preload медиа (pako, Lottie) и TTS для стабильного отображения донатов в эфире.

POTALONU / PREEGLOS — билетный сервис и схема зала (Next.js 16, React 19, TypeScript, PostgreSQL, Drizzle ORM, Auth.js, Docker, Docker Compose, GitLab CI/CD)

- Реализовал web-часть билетного продукта: витрина событий, сценарии покупки билетов, Telegram Mini App (`@twa-dev/sdk`) и клиентские формы на React Hook Form + Zod.
- Спроектировал и собрал seatmap-studio (PREEGLOS): редактор залов `/halls/.../editor`, embed-виджет `/embed/[hallId]`, события и бронирования; Next.js 16, PostgreSQL, Drizzle ORM, Auth.js.
- Настроил self-hosted поставку seatmap-сервиса: Docker/Docker Compose, pipeline в GitLab CI/CD (test, build image, deploy), выкатка на stage с nginx.

### X5 Tech — Frontend-разработчик

04.2024 – 07.2025 | Удаленно

- Спроектировал и реализовал модуль согласования закупочных процедур (НКЗ 3.0): role-based access, статусы, переходы состояний, черновики и восстановление пользовательских сценариев.
- Интегрировал авторизацию через Keycloak: SSO, роли и доступ к модулям согласования по матрице RBAC.
- Внедрил Orval для генерации типов и API‑клиента по OpenAPI, убрал ручное обновление контрактов и снизил количество ошибок на стыке фронтенда и backend.
- Реализовал формы и сценарии редактирования на react-hook-form, развивал внутренний UI Kit и единые паттерны для интерфейсов сервиса.
- Оптимизировал сборку на Vite (code splitting, dynamic imports), улучшив скорость начальной загрузки и отзывчивость приложения на длинных сценариях согласования.

### BI.ZONE — Frontend-разработчик

06.2023 – 03.2024 | Удаленно

- Развивал продукт Thread Intelligence: React 16, TypeScript, Webpack, MobX, React Query, React Hook Form, axios, styled-components, BEM, компоненты @bizone, i18next; клиент по OpenAPI через Orval; GraphQL через Apollo Client.
- Реализовал страницу анализа сущностей: граф связей на Cytoscape.js, сложные фильтры и сценарии для аналитиков.
- Динамические отчёты и дашборды: Highcharts, Recharts, react-grid-layout; тяжёлые списки и сетки — react-virtualized, @tanstack/react-virtual, lazy loading.
- Модуль динамических отчётов на GraphQL (Apollo Client), связанный с аналитической моделью данных и существующими сценариями Thread Intelligence.

### НЛМК — Frontend-разработчик

05.2022 – 06.2023 | Удаленно

- Спроектировал и реализовал веб‑приложение “Регистрация выпусков чугуна” для доменного производства, переведя ключевые операции из разрозненных ручных процессов в единый интерфейс.
- Настроил вход и разграничение доступа через Keycloak (SSO, роли, защита API-маршрутов).
- Реализовал role-based сценарии работы с производственными данными и сложные интерактивные таблицы на TanStack Table: сортировка, фильтрация, пагинация, работа с большими объёмами данных.
- Настроил клиентское кэширование и фоновые обновления через React Query, снизив нагрузку на API и сделав работу с данными более предсказуемой.
- Интегрировал Sentry для мониторинга ошибок и диагностики проблем в продакшене.

### Citilink — Frontend-разработчик

04.2021 – 04.2022 | Удаленно

- Участвовал в миграции легаси‑разделов e‑commerce сайта с PHP/Symfony на Next.js, включая каталог и главную страницу.
- Разработал клиентскую логику каталога: фильтрация, сортировка, пагинация, состояние URL, сохранение пользовательских параметров, загрузка данных через REST API.
- Оптимизировал структуру компонентов и взаимодействие с API, повысив предсказуемость состояния приложения и стабильность пользовательских сценариев.
- Работал на стыке фронтенда, легаси‑бэкенда и микросервисов, согласовывал API‑контракты и перенос функционала в новую версию сайта.


## Навыки

- Языки: TypeScript, JavaScript (ES6+), HTML5, CSS3/SCSS
- Frontend‑стек: React, Next.js (SSR/SSG), Redux Toolkit, Redux‑Saga, MobX, React Query (TanStack Query), TanStack Table, React Hook Form, Zod, Formik, react-router, Framer Motion, Radix UI, Tailwind CSS
- Сложные интерфейсы и визуализация: Cytoscape.js, Highcharts, Recharts, react-grid-layout, react-virtualized, @tanstack/react-virtual, Canvas
- Сборка и инфраструктура фронтенда: Vite, Webpack, Git, монорепозитории, code splitting, dynamic imports, tree shaking, CI/CD, GitHub Actions, GitLab CI/CD, Jenkins, Docker, Docker Compose, Coolify
- Интеграции и бэкенд: REST API, GraphQL (Apollo Client), OpenAPI/Orval, WebSocket, Socket.io, WebRTC, Keycloak, Nest.js (REST, модули, DTO, TypeORM), Drizzle ORM, PostgreSQL, Firebase (Auth, Functions), Auth.js, JWT/Passport, Node.js, Symfony, Bitrix, jQuery
- Наблюдаемость и качество: Sentry, Kibana, Grafana, Jest, Vitest, Playwright
- UI и продукт: дизайн‑системы и UI Kit, Material UI, styled-components, BEM, i18next, Telegram Mini Apps, Figma

## Языки

- Английский — B1

## Образование и сообщество

### Тульский государственный коммунально-строительный техникум

Земельно-имущественные отношения · 2015 – 2018 | Тула, Россия

### Компьютерная академия «ШАГ»

Веб-разработка · 2016 | Тула, Россия

Хакатоны и профессиональная активность: победитель хакатона «Цифровой прорыв» (2021, 2020), победитель Hack.Genesis _ONLINE_, финалист Virus Hack, эксперт чемпионата WorldSkills.

