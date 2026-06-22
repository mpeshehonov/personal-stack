# Максим Пешехонов

Senior Frontend-разработчик

Удалённо, РФ · Email: kassady71@gmail.com · Телефон: +79509196786 · Сайт: [mpeshekhonov.ru](https://mpeshekhonov.ru/ru) · [Telegram: `@makusimu_san`](https://t.me/makusimu_san) · [LinkedIn: `makusimu`](https://www.linkedin.com/in/makusimu) · [GitHub: `mpeshehonov`](https://github.com/mpeshehonov) · Дата рождения: 28.05.1996

**Готов к выходу ASAP.**

## О себе

Senior Frontend-разработчик, 7+ лет: React, TypeScript, Next.js для enterprise-сервисов, e-commerce, real-time интерфейсов и Telegram Mini Apps. Специализируюсь на сложных пользовательских сценариях: роли и права, длинные формы, typed API-контракты, GraphQL/REST, WebSocket и дизайн-системы.

Сильнее всего полезен там, где frontend — не набор экранов, а часть продуктовой архитектуры: нужно договориться об API, разложить фичу на понятные модули, пройти code review и довести до production.

## Опыт работы

### POTALONU LLC — Frontend-разработчик

09.2025 – 06.2026 | Удалённо

**sendonate.com**: React-продукт для стримеров: Mini App, кабинет, OBS overlay

Роль: Спроектировал frontend-контур sendonate.com из трёх React + Vite + TypeScript клиентов: кабинет стримера, Telegram Mini App и OBS overlay. Развивал дизайн виджетов донатов и сценарии кабинета, завёл типизированный REST-клиент через Orval/OpenAPI, real-time доставку событий по WebSocket и CI/CD для lint/build/deploy всех клиентов из одного репозитория.

Результат:

- End-to-end сценарий доната доведён до production: Mini App, backend, кабинет стримера и alert в OBS overlay работают как один продуктовый флоу
- WebSocket-оверлей обрабатывает последовательные донаты через очередь алертов и reconnect без ручного обновления эфира
- Orval и общий delivery pipeline уменьшают рассинхрон между клиентами и backend при изменении API-контрактов

Стек: React, TypeScript, Vite, REST API, Orval, WebSocket, Django REST, GitHub Actions, Sentry

**POTALONU / PREEGLOS**: Интернет-витрина билетов и редактор схем залов

Роль: Реализовал web-витрину PREEGLOS на Next.js с checkout-сценарием, Auth.js, PostgreSQL/Drizzle и типизированным REST-клиентом через Orval. Отдельно собрал сервис для схем залов: редактор, хранение структуры мест и embeddable seat picker для партнёрских сайтов; настроил GitLab CI/CD и Docker Compose delivery.

Результат:

- Организаторы могут заводить залы и продавать места через виджет без ручной отрисовки схем под каждое событие
- Покупка билета в вебе и Telegram Mini App работает на общей модели данных и API-контрактах
- Production delivery через Docker Compose и GitLab pipeline снижает количество ручных операций при выкладке

Стек: Next.js, React, TypeScript, PostgreSQL, SQL, Orval, Docker, GitLab CI, Auth.js

### X5 Tech — Frontend-разработчик

04.2024 – 07.2025 | Удалённо

**НКЗ 3.0 — согласование закупок**: Enterprise React-модуль: RBAC, статусы, длинные формы

Роль: Развивал enterprise-модуль согласования закупок на React + TypeScript: ролевой доступ через Keycloak SSO, многошаговые формы на react-hook-form, типизированный API-слой через Orval/OpenAPI и компоненты из внутреннего npm UI Kit. Делал задачу перехода сборки на Vite, участвовал в декомпозиции, code review и выносил тяжёлые сценарии в отдельные chunks.

Результат:

- Frontend закрывает полный цикл закупочного согласования: роли, статусы, формы и переходы между этапами
- OpenAPI/Orval сделал API-контракты проверяемыми на сборке и снизил зависимость от ручного обновления типов
- Переход на Vite, code splitting и миграция тестового контура с React Testing Library на Vitest помогли ускорить разработку и проверки

Стек: React, TypeScript, JavaScript, Vite, REST API, Orval, Keycloak, Git, react-hook-form, React Testing Library

### BI.ZONE — Frontend-разработчик

06.2023 – 03.2024 | Удалённо

**Threat Intelligence**: React + GraphQL: аналитика связей для SOC

Роль: Развивал аналитический интерфейс для SOC на React + TypeScript: GraphQL/Apollo для основной модели данных, MobX/React Query для состояния и запросов, D3.js для графа связей, виртуализация для больших списков и Jest для регрессионных проверок. Участвовал в code review, доработке UX сложных аналитических сценариев и оптимизации тяжёлых экранов.

Результат:

- Граф связей, фильтры и отчёты объединены в одном рабочем экране аналитика
- Единый GraphQL/Apollo data layer для аналитики и отчётов — меньше расхождений между экраном и выгрузками
- Виртуализация сохраняет отзывчивость интерфейса на больших списках сущностей

Стек: React, TypeScript, GraphQL, REST API, D3.js, Jest, Git

### НЛМК — Frontend-разработчик

05.2022 – 06.2023 | Удалённо

**Регистрация выпусков чугуна**: React SPA вместо Excel для производственных данных

Роль: Разработал production SPA для регистрации выпусков чугуна на React + TypeScript: таблицы и фильтры на TanStack Table, серверное состояние через React Query, Keycloak SSO/RBAC для доступа по ролям. Подключил GitLab CI checks на merge request и Sentry для диагностики production-ошибок.

Результат:

- Ключевые операции смены переведены из Excel в web-интерфейс с авторизацией и ролевыми правами
- Таблицы, фильтры и серверное состояние рассчитаны на производственные объёмы данных и работу по сменам
- Sentry даёт production visibility: ошибки привязаны к релизам и стек-трейсам без воспроизведения на рабочем месте

Стек: React, TypeScript, TanStack Table, TanStack Query, REST API, Keycloak, GitLab CI, Sentry

### Citilink — Frontend-разработчик

04.2021 – 04.2022 | Удалённо

**citilink.ru — каталог интернет-магазина**: Миграция e-commerce с PHP/Symfony на Next.js + React

Роль: Участвовал в миграции e-commerce каталога и главной citilink.ru с PHP/Symfony на React + Next.js: фильтрация, сортировка, пагинация и URL-состояние для SEO и шаринга. Интегрировал REST API backend/микросервисов, работал в yarn workspaces монорепо, покрывал критичную логику Jest-тестами и проходил code review.

Результат:

- SEO-контур каталога сохранён при миграции на Next.js: индексируемые страницы и URL-состояние фильтров
- Retail/wholesale сценарии через синхронизацию фильтров, сортировки и пагинации с URL
- Shared npm-пакеты в yarn workspaces помогали переиспользовать логику между страницами каталога и главной

Стек: Next.js, React, TypeScript, JavaScript, REST API, Redux, Jest, Git

## Навыки

- **Языки:** TypeScript, JavaScript (ES6+), HTML5, CSS3, SCSS/SASS, Python, Node.js
- **Frontend:** React, Next.js (SSR/SSG), Gatsby, Redux Toolkit, MobX, TanStack Query, TanStack Table, React Hook Form, Zod, react-router, Feature-Sliced Design, Module Federation, Tailwind CSS, CSS-in-JS / Emotion, jQuery, адаптивная вёрстка
- **CMS:** Contentful, Strapi, WordPress, 1C-Bitrix, headless CMS, интеграции CMS с Next.js/Node.js
- **Сборка и Git:** Git, Webpack, Vite, yarn workspaces, монорепозитории, npm-пакеты, code splitting, GitLab CI, GitHub Actions, Docker, CI/CD
- **API и backend:** REST API, OpenAPI/Orval, GraphQL (Apollo Client), WebSocket, PHP, Symfony, MySQL, PostgreSQL, SQL, Drizzle ORM, Nest.js, Django REST, компоненты и шаблоны Bitrix, Keycloak, Auth.js
- **Качество и процессы:** Jest, Vitest, React Testing Library, Playwright, Storybook, Sentry, code review, Scrum, Agile
- **UI & продукт:** e-commerce, дизайн-системы, UI Kit, Material UI, Figma, Telegram Mini Apps, i18next, next-intl

## Иностранные языки

- Английский — B1

## Образование и сообщество

### Тульский государственный коммунально-строительный техникум

Земельно-имущественные отношения · 2015 – 2018 | Тула, Россия

### Компьютерная академия «ШАГ»

Веб-разработка · 2016 | Тула, Россия

Победитель хакатона «Цифровой прорыв» (2021, 2020), победитель Hack.Genesis _ONLINE_, финалист Virus Hack, эксперт чемпионата WorldSkills.
