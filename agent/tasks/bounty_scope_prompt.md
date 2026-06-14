# Phase 1 — Scope mapping

Программа:
- **Name:** {program_name}
- **Platform:** {platform}
- **URL:** {program_url}
- **Team handle:** {team_handle}
- **Focus:** {program_focus}

## Задача
Собери **in-scope** и **out-of-scope** для bug bounty. Это фаза 1 из 4 — только разведка scope.

## Обязательные действия
1. `curl -fsSL` policy/scope страницы программы (и linked policy docs если есть).
2. Найди публичные assets: домены, API, приложения, GitHub repos если in-scope.
3. Выпиши явные **out-of-scope** правила.

## Формат ответа (RU + JSON)

**Research log:** что нашёл, какие URL проверил, 5–10 in-scope assets.

```json
{{
  "phase": "scope",
  "in_scope_assets": ["https://..."],
  "out_of_scope": ["..."],
  "policy_urls": ["https://..."],
  "notes": "краткий вывод для следующей фазы"
}}
```

Не переходи к эксплуатации — только scope. Запускай реальные curl/http запросы.
