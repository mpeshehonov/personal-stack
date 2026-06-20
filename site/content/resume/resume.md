# Максим Пешехонов

Senior Frontend-разработчик

Сочи, Россия · Email: kassady71@gmail.com · Телефон: +79509196786 · Сайт: [mpeshekhonov.ru](https://mpeshekhonov.ru/ru) · [Telegram: `@makusimu_san`](https://t.me/makusimu_san) · [LinkedIn: `makusimu`](https://www.linkedin.com/in/makusimu) · [GitHub: `mpeshehonov`](https://github.com/mpeshehonov) · Дата рождения: 28.05.1996

**Готов к выходу ASAP.**

## О себе

Senior Frontend-разработчик, 7+ лет: React, TypeScript, Next.js для e-commerce, enterprise-модулей и продуктовых интерфейсов. Проектирую сложные UI, связываю frontend с typed API-контрактами и довожу фичи до production через review и CI/CD.

Другие задачи и кейсы — в разделе Проекты на сайте. Backend-интеграция: Django REST, Nest.js, PostgreSQL, SQL. Сочи, удалённо. Готов к выходу ASAP.

## Опыт работы

### POTALONU LLC — Frontend-разработчик

09.2025 – н.в. | Удалённо

**sendonate.com**: React-продукт для стримеров: Mini App, кабинет, OBS overlay

Роль: Спроектировал и реализовал frontend-контур sendonate.com из трёх React + Vite + TypeScript клиентов: кабинет стримера, Telegram Mini App и OBS overlay. Завёл типизированный REST-клиент через Orval/OpenAPI, real-time доставку событий по WebSocket и CI/CD в GitHub Actions для lint/build/deploy всех клиентов из одного репозитория.

Результат:

- End-to-end сценарий доната до production: Mini App → backend → alert в OBS overlay без ручного обновления эфира
- Orval генерирует DTO и методы API из OpenAPI-контракта — рассинхрон frontend/backend ловится на сборке
- Единый delivery pipeline для трёх клиентов: автоматические проверки, сборка и деплой без ручных операций

Стек: React, TypeScript, Vite, REST API, Orval, WebSocket, Django REST, GitHub Actions

**POTALONU / PREEGLOS**: Интернет-витрина билетов и редактор схем залов

Роль: Реализовал web-витрину PREEGLOS на Next.js с checkout-сценарием, Auth.js, PostgreSQL/Drizzle и типизированным REST-клиентом через Orval. Отдельно собрал редактор схем залов на Canvas/SVG и embeddable seat picker для партнёрских сайтов; настроил GitLab CI/CD и Docker Compose delivery.

Результат:

- Покупка билета в вебе и Telegram Mini App на общей модели данных и API-контрактах
- Партнёры подключают seat picker без форка продукта: схема зала и выбор мест в одном frontend-контуре
- Production delivery: Docker Compose окружение и GitLab pipeline собирают и выкатывают сервис без ручной сборки

Стек: Next.js, React, TypeScript, PostgreSQL, SQL, Orval, Docker, GitLab CI

### X5 Tech — Frontend-разработчик

04.2024 – 07.2025 | Удалённо

**НКЗ 3.0 — согласование закупок**: Enterprise React-модуль: RBAC, статусы, длинные формы

Роль: Разрабатывал enterprise-модуль согласования закупок на React + TypeScript: ролевой доступ через Keycloak SSO, многошаговые формы на react-hook-form, типизированный API-слой через Orval/OpenAPI и компоненты из внутреннего npm UI Kit. Участвовал в code review и выносил тяжёлые сценарии в отдельные chunks через Vite code splitting.

Результат:

- Frontend закрывает полный цикл закупочного согласования: роли, статусы, формы и переходы между этапами
- OpenAPI/Orval сделал API-контракты проверяемыми на сборке вместо ручного обновления типов
- Vite code splitting разделил тяжёлые approval-сценарии на независимые чанки и снизил риск регрессий

Стек: React, TypeScript, JavaScript, Vite, REST API, Orval, Keycloak, Git

### BI.ZONE — Frontend-разработчик

06.2023 – 03.2024 | Удалённо

**Threat Intelligence**: React + GraphQL: аналитика связей для SOC

Роль: Развивал аналитический интерфейс для SOC на React + TypeScript: GraphQL/Apollo для основной модели данных, MobX/React Query для состояния и запросов, D3.js для графа связей, виртуализация для больших списков и Jest для регрессионных проверок. Участвовал в code review и доработке UX сложных аналитических сценариев.

Результат:

- Граф связей, фильтры и отчёты объединены в одном рабочем экране аналитика
- Единый GraphQL data layer для аналитики и отчётов — меньше расхождений между экраном и выгрузками
- Виртуализация сохраняет отзывчивость интерфейса на больших списках сущностей

Стек: React, TypeScript, GraphQL, REST API, D3.js, Jest, Git

### НЛМК — Frontend-разработчик

05.2022 – 06.2023 | Удалённо

**Регистрация выпусков чугуна**: React SPA вместо Excel для производственных данных

Роль: Разработал production SPA для регистрации выпусков чугуна на React + TypeScript: таблицы и фильтры на TanStack Table, серверное состояние через React Query, Keycloak SSO/RBAC для доступа по ролям. Подключил GitLab CI checks на merge request и Sentry для диагностики production-ошибок.

Результат:

- Ключевые операции смены переведены из Excel в web-интерфейс с авторизацией и ролевыми правами
- Таблицы и фильтры пригодны для производственных объёмов данных
- Sentry даёт production visibility: ошибки привязаны к релизам и стек-трейсам без воспроизведения на рабочем месте

Стек: React, TypeScript, TanStack Table, TanStack Query, REST API, Keycloak, GitLab CI, Sentry

### Citilink — Frontend-разработчик

04.2021 – 04.2022 | Удалённо

**citilink.ru — каталог интернет-магазина**: Миграция e-commerce с PHP/Symfony на Next.js + React

Роль: Участвовал в миграции e-commerce каталога и главной citilink.ru с PHP/Symfony на React + Next.js: фильтрация, сортировка, пагинация и URL-состояние для SEO и шаринга. Интегрировал REST API backend/микросервисов, работал в yarn workspaces монорепо, покрывал критичную логику Jest-тестами и проходил code review.

Результат:

- SEO-контур каталога сохранён при миграции на Next.js: индексируемые страницы и URL-состояние фильтров
- Retail/wholesale сценарии через синхронизацию фильтров, сортировки и пагинации с URL
- Shared npm-пакеты в yarn workspaces снизили дублирование между страницами каталога

Стек: Next.js, React, TypeScript, JavaScript, REST API, Redux, Jest, Git

## Навыки

- **Языки:** TypeScript, JavaScript (ES6+), HTML5, CSS3, SCSS/SASS, Python, Node.js
- **Frontend:** React, Next.js (SSR/SSG), Gatsby, Redux Toolkit, MobX, TanStack Query, TanStack Table, React Hook Form, Zod, react-router, Tailwind CSS, jQuery, адаптивная вёрстка
- **CMS:** Contentful, Strapi, WordPress, 1C-Bitrix, headless CMS, интеграции CMS с Next.js/Node.js
- **Сборка и Git:** Git, Webpack, Vite, yarn workspaces, монорепозитории, npm-пакеты, code splitting, GitLab CI, GitHub Actions, Docker, CI/CD
- **API и backend:** REST API, OpenAPI/Orval, GraphQL (Apollo Client), WebSocket, PHP, Symfony, MySQL, PostgreSQL, SQL, Drizzle ORM, Nest.js, Django REST, компоненты и шаблоны Bitrix, Keycloak, Auth.js
- **Качество и процессы:** Jest, Vitest, Playwright, Sentry, code review, Scrum, Agile
- **UI & продукт:** e-commerce, дизайн-системы, UI Kit, Material UI, Figma, Telegram Mini Apps, i18next, next-intl

## Иностранные языки

- Английский — B1

## Образование и сообщество

### Тульский государственный коммунально-строительный техникум

Земельно-имущественные отношения · 2015 – 2018 | Тула, Россия

### Компьютерная академия «ШАГ»

Веб-разработка · 2016 | Тула, Россия

Победитель хакатона «Цифровой прорыв» (2021, 2020), победитель Hack.Genesis _ONLINE_, финалист Virus Hack, эксперт чемпионата WorldSkills.
