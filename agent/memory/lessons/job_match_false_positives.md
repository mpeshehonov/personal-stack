# Job matcher: false positives (2026-07-21, updated 2026-07-30)

После первого career-hunter scan: высокий `match_score` ≠ хороший shortlist.

## Паттерны

| Сигнал в тексте | Почему врёт score | Что делать в `/jobs` |
|-----------------|-------------------|----------------------|
| `React Native` / mobile-only | Title содержит React → +15 stack; web FE profile не матчится | dislike, если нет RN в резюме |
| Тег `#middle` при score 90+ | Senior keywords в skills, уровень роли ниже | dislike / skip |
| Агентство + emoji + «от 2 лет» | Title «Frontend» + remote поднимает score | dislike; ниже $3–4k bar |
| Hirify без company name | Title/skills сильные, employer пустой | смотреть карточку; **не** штрафовать источник — с 2026-07-30 «Мимо» на Hirify = paywall по умолчанию; для плохого fit: `/jobs dislike <id> bad_fit` |
| Hirehi generic title + вилка ~450k–950k₽ | `remote (+10)` + `вилка (+12)` → score ~77 без стека/senior в title | смотреть snippet «middle/senior»; agency / inflated fork = skip |
| Habr Senior/Lead + Москва офис/гибрид | Title senior (+20) при `не remote (−8)` всё ещё ≥70 | shortlist только если гибрид/офис ОКемлем |
| «от 2 лет» без #senior (CIS TG) | React/TS overlap даёт 80+ без senior bar | ниже приоритета shortlist |
| Офис регион (Барнаул и т.п.) | Стек сильный, локация не remote | skip |
| Proglib / feed «подборка» / дайджест | Title содержит Frontend → score 70+ | dislike; не одна вакансия |
| Повтор employer после dislike на другой доске | BlueThrone disliked на hirify, снова на hirehi | skip / dislike снова |
| Кросс-канал TG дубль (frontend_rabota ↔ job_react) | Один пост → два lead id; count растёт без нового сигнала | shortlist по компании+роли; дубль RN после dislike (#48→#60) = skip |
| Повторный репост того же поста в одном канале (#46/#58/#65 VK) | Новый id, тот же employer+роль | skip; не считать «новым» shortlist |
| Senior + `#офис` Москва (МТС и т.п.) | Title senior (+20) держит score ≥70 при office | skip, если remote-only |
| Один работодатель, разные роли (WB #44 платформа 72 vs #66 маркетплейс 100) | Низкий score без #senior ≠ отмена бренда | смотреть новую карточку отдельно |
| Title «Frontend» + Angular (Т-Банк #69) | `frontend` в названии (+15) без React-стека | mismatch — не путать с React-ролью того же бренда (#45) |
| Middle/Senior + `#офис` (ВкусВилл #68) | «Senior» в title (+20) держит score при office | skip, если remote-only |
| Marketplace FE без `#senior` (OZON #67) | remote (+10) + Frontend title → ≥70 при «от 3 лет» | watch / низкий приоритет vs явный senior remote |
| Fullstack `.Net+React` / backend-primary (Альфа #70) | `React` в title (+15) + remote (+10) при основном .Net/backend | mismatch vs Senior FE target; не like автоматически |
| «Ведущий» / Senior + `#офис` банк (АТБ #71 Цифровой рубль) | ведущ/senior (+20) + React держит ≥80 при office Москва | skip, если remote-only — тот же паттерн, что X5/ВкусВилл office |
| Title Frontend + Vue/Nuxt (AGIMA #73 proglib) | `frontend` (+15) + TS/Vite/Git overlap (+15) + remote (+10) → 88 без React | mismatch — смотреть стек в snippet; Vue ≠ React shortlist |
| Репост без #senior (Облако.ру #56/#62/#72/#80/#93) | тот же employer+роль, «от 2 лет», score 82; уже 5 id | skip как дубль; не поднимать в like |
| Habr + Hirehi один employer (РГС #91/#92, рядом #53) | два lead id / два score (74 vs 79 remote) без нового сигнала | один сигнал на компанию+роль; prefer remote card |
| Батч-зеркало каналов (#74–78 = #64–68) | Оркестратор подтянул те же посты из второго TG-канала одним сканом | shortlist не менять; считать одним сигналом на employer+роль |
| Senior FE + Vue 3 в snip (МТС NBA.Банк #74/#64) | Title Senior (+20) + TS overlap при стеке Vue + `#офис` | mismatch — Vue ≠ React; office skip |

## Правило для агента

В daily shortlist явно помечать **mismatch** (RN / middle / office-only / agency spam / digest / cross-channel dupe), даже при score ≥90. Не предлагать «топ» только по числу.
