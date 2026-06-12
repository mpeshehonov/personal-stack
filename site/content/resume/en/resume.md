# Maksim Peshekhonov

Senior Frontend Engineer

Sochi, Russia · Email: kassady71@gmail.com · Phone: +79509196786 · [Telegram: `@makusimu_san`](https://t.me/makusimu_san) · [LinkedIn: `makusimu`](https://www.linkedin.com/in/makusimu) · [GitHub: `mpeshehonov`](https://github.com/mpeshehonov) · Date of birth: 28.05.1996

## About

Senior Frontend / Fullstack engineer since 2018: B2B, e-commerce, marketplaces, real-time, and Telegram Mini Apps. I build UIs with complex flows, RBAC, Orval/OpenAPI, and REST, GraphQL, and WebSocket integrations.

Full case list on the Projects page; detailed PDF on request.

Core stack: Next.js, React, TypeScript, Vite, TanStack Query, Orval + OpenAPI, React Hook Form, Zod, Radix UI, Tailwind CSS, Sentry, Playwright. For fullstack work I use Nest.js (REST, DTOs, Socket.io gateways, TypeORM, PostgreSQL) and REST integrations.

Highlights: X5 Tech — procurement approval with RBAC; NLMK — production data app; BI.ZONE — Thread Intelligence; Citilink — Symfony to Next.js migration; POTALONU — sendonate.com and PREEGLOS seat maps.

## Work experience

### POTALONU LLC — Fullstack / Frontend engineer

Sep 2025 – present | Remote

sendonate.com — tipping for streamers (React 19, Vite, TypeScript, Telegram Mini App, REST, OpenAPI/Orval, TanStack Query, React Hook Form, Zod, Sentry)

- Designed and built three client surfaces: streamer web dashboard on React 19 + Vite + TanStack Query + Orval + React Hook Form + Zod + Sentry, Telegram Mini App on @telegram-apps/sdk + Vite, and a separate Vite bundle for OBS / live overlay.
- Implemented the full tipping flow: Mini App checkout, REST via Orval from OpenAPI, dashboard with CRUD collections, pagination, debounced search, and alert settings.
- Built a real-time overlay on WebSocket with reconnect, alert queue, media preload (pako, Lottie), and TTS so tips render reliably on stream under bursty events.

POTALONU / PREEGLOS — ticketing platform and seat map (Next.js 16, React 19, TypeScript, PostgreSQL, Drizzle ORM, Auth.js, Docker, Docker Compose, GitLab CI/CD)

- Implemented ticketing web flows: events storefront, checkout, Telegram Mini App (`@twa-dev/sdk`), forms with React Hook Form + Zod.
- Built seatmap-studio: hall editor, embed seat picker, events and bookings; Next.js 16, PostgreSQL, Drizzle ORM, Auth.js.
- Self-hosted delivery: Docker Compose, GitLab CI/CD (test, build, deploy), stage on nginx.

### X5 Tech — Frontend engineer

Apr 2024 – Jul 2025 | Remote

- Designed and delivered the procurement approval module (NKZ 3.0): RBAC, statuses, state transitions, drafts, and restoring user flows.
- Integrated Keycloak authorization: SSO, roles, and RBAC matrix for module access.
- Introduced Orval for types and API client from OpenAPI, removing manual contract updates and reducing front/back integration bugs.
- Built forms and editing flows with react-hook-form, extended the internal UI kit and shared UI patterns.
- Optimized the Vite build (code splitting, dynamic imports), improving initial load and responsiveness on long approval paths.

### BI.ZONE — Frontend engineer

Jun 2023 – Mar 2024 | Remote

- Shipped features for Thread Intelligence: React 16, TypeScript, Webpack, MobX, React Query, React Hook Form, axios, styled-components, BEM, @bizone components, i18next; OpenAPI client via Orval; GraphQL with Apollo Client.
- Built entity analysis: relationship graphs on Cytoscape.js, advanced filters and analyst workflows.
- Dynamic reports and dashboards: Highcharts, Recharts, react-grid-layout; heavy lists and grids with react-virtualized, @tanstack/react-virtual, lazy loading.
- Dynamic reporting module on GraphQL (Apollo Client) tied to the analytics data model and existing Thread Intelligence workflows.

### NLMK — Frontend engineer

May 2022 – Jun 2023 | Remote

- Delivered the “Pig iron batch registration” web app for blast-furnace production, consolidating fragmented manual steps into one interface.
- Configured sign-in and access control with Keycloak (SSO, roles, protected API routes).
- Implemented RBAC over production data and complex tables on TanStack Table: sort, filter, pagination, large datasets.
- Used React Query for caching and background refresh, reducing API load and stabilizing UX.
- Integrated Sentry for error monitoring in production.

### Citilink — Frontend engineer

Apr 2021 – Apr 2022 | Remote

- Helped migrate legacy e‑commerce sections from PHP/Symfony to Next.js, including catalog and home.
- Built catalog UX: filters, sort, pagination, URL state, user preferences, REST-backed data loading.
- Refined component structure and API usage for more predictable state and stable flows.
- Worked across frontend, legacy backend, and microservices; aligned API contracts for the new site.

### In2View — Fullstack / Frontend engineer

Feb 2018 – Mar 2021 | Remote

- Built the In2View B2B platform for respondent discovery and customer-development research: React, Redux Toolkit, Firebase, Vite, Formik, react-router, i18next; marketing site on Gatsby + Contentful with Framer Motion.
- Implemented matching between respondents and clients from reference profiles; end-to-end client and server logic with REST API, JWT, and role-based access.
- Shipped PWA and two-factor auth via Firebase Authentication; reports, tables, filters, and aggregations for corporate users.
- Owned the production MVP: application architecture, RBAC, data storage; evolved codebase structure as the product grew.

## Skills

- Languages: TypeScript, JavaScript (ES6+), HTML5, CSS3/SCSS
- Frontend: React, Next.js (SSR/SSG), Redux Toolkit, Redux-Saga, MobX, React Query (TanStack Query), TanStack Table, React Hook Form, Zod, Formik, react-router, Framer Motion, Radix UI, Tailwind CSS
- Complex UI & data visualization: Cytoscape.js, Highcharts, Recharts, react-grid-layout, react-virtualized, @tanstack/react-virtual, Canvas
- Build & frontend infra: Vite, Webpack, Git, monorepos, code splitting, dynamic imports, tree shaking, CI/CD, GitHub Actions, GitLab CI/CD, Jenkins, Docker, Docker Compose, Coolify
- Integrations & backend: REST API, GraphQL (Apollo Client), OpenAPI/Orval, WebSocket, Socket.io, WebRTC, Keycloak, Nest.js (REST, modules, DTOs, TypeORM), Drizzle ORM, PostgreSQL, Firebase (Auth, Functions), Auth.js, JWT/Passport, Node.js, Symfony, Bitrix, jQuery
- Observability & quality: Sentry, Kibana, Grafana, Jest, Vitest, Playwright
- UI & product: design systems and UI kits, Material UI, styled-components, BEM, i18next, Telegram Mini Apps, Figma

## Languages

- English — B1
- Russian — native

## Education & community

### Tula State Municipal Construction College

Land and property (vocational) · 2015 – 2018 | Tula, Russia

### Computer Academy STEP

Web development · 2016 | Tula, Russia

Hackathons & community: winner, Digital Breakthrough (2021, 2020); winner, Hack.Genesis ONLINE; finalist, Virus Hack; expert, WorldSkills.
