# Job matcher: false positives (2026-07-21, updated 2026-07-25)

После первого career-hunter scan: высокий `match_score` ≠ хороший shortlist.

## Паттерны

| Сигнал в тексте | Почему врёт score | Что делать в `/jobs` |
|-----------------|-------------------|----------------------|
| `React Native` / mobile-only | Title содержит React → +15 stack; web FE profile не матчится | dislike, если нет RN в резюме |
| Тег `#middle` при score 90+ | Senior keywords в skills, уровень роли ниже | dislike / skip |
| Агентство + emoji + «от 2 лет» | Title «Frontend» + remote поднимает score | dislike; ниже $3–4k bar |
| Hirify без company name | Title/skills сильные, employer пустой | смотреть карточку; вес hirify уже 0.25 / off после dislikes |
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

## Правило для агента

В daily shortlist явно помечать **mismatch** (RN / middle / office-only / agency spam / digest / cross-channel dupe), даже при score ≥90. Не предлагать «топ» только по числу.
