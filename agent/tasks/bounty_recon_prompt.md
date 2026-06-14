# Phase 2 — Recon on in-scope assets

Программа: **{program_name}** ({platform}) — {program_url}

## Контекст предыдущей фазы (scope)
{prior_context}

## Задача
Для **3–5 in-scope assets** из scope-фазы собери поверхность атаки.

## Обязательные действия (минимум 3 asset)
Для каждого asset:
1. `curl -fsSI` / HEAD — статус, headers, tech hints
2. Публичные JS/API endpoints (view-source, `/api`, swagger/openapi если есть)
3. Auth flows: login, OAuth, session cookies — **без** brute-force
4. Запиши **конкретные URL/path** для тестирования в фазе 3

## Формат ответа

**Research log (RU):** таблица asset → endpoints → интересные точки.

```json
{{
  "phase": "recon",
  "assets_profiled": [
    {{
      "url": "https://...",
      "endpoints": ["/api/v1/...", "..."],
      "auth": "session|oauth|none|api-key",
      "attack_surface": "кратко"
    }}
  ],
  "hypothesis_seeds": [
    "IDOR on /api/...",
    "XSS in ...",
    "SSRF via ..."
  ],
  "notes": "что приоритетно для hunt"
}}
```

Запускай реальные команды. Не выдумывай endpoints без проверки.
