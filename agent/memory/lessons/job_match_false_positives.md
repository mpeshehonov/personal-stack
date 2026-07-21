# Job matcher: false positives (2026-07-21)

После первого career-hunter scan: высокий `match_score` ≠ хороший shortlist.

## Паттерны

| Сигнал в тексте | Почему врёт score | Что делать в `/jobs` |
|-----------------|-------------------|----------------------|
| `React Native` / mobile-only | Title содержит React → +15 stack; web FE profile не матчится | dislike, если нет RN в резюме |
| Тег `#middle` при score 90+ | Senior keywords в skills, уровень роли ниже | dislike / skip |
| Агентство + emoji + «от 2 лет» | Title «Frontend» + remote поднимает score | dislike; ниже $3–4k bar |
| Hirify без company name | Title/skills сильные, employer пустой | смотреть карточку; один dislike уже снизил вес hirify |

## Правило для агента

В daily shortlist явно помечать **mismatch** (RN / middle / office-only / agency spam), даже при score ≥90. Не предлагать «топ» только по числу.
