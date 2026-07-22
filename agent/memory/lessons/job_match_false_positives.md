# Job matcher: false positives (2026-07-21, updated 2026-07-22)

После первого career-hunter scan: высокий `match_score` ≠ хороший shortlist.

## Паттерны

| Сигнал в тексте | Почему врёт score | Что делать в `/jobs` |
|-----------------|-------------------|----------------------|
| `React Native` / mobile-only | Title содержит React → +15 stack; web FE profile не матчится | dislike, если нет RN в резюме |
| Тег `#middle` при score 90+ | Senior keywords в skills, уровень роли ниже | dislike / skip |
| Агентство + emoji + «от 2 лет» | Title «Frontend» + remote поднимает score | dislike; ниже $3–4k bar |
| Hirify без company name | Title/skills сильные, employer пустой | смотреть карточку; один dislike уже снизил вес hirify |
| Hirehi generic title + вилка ~450k₽ | `remote (+10)` + `вилка (+12)` → score ~77 без стека/senior в title | смотреть snippet «middle/senior»; agency = skip |
| Proglib «подборка» / дайджест | Title содержит Frontend → score 70+ | dislike; не одна вакансия |
| Повтор employer после dislike на другой доске | BlueThrone disliked на hirify, снова на hirehi | skip / dislike снова |

## Правило для агента

В daily shortlist явно помечать **mismatch** (RN / middle / office-only / agency spam / digest), даже при score ≥90. Не предлагать «топ» только по числу.
