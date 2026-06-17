# Phase 3 — Active hunting (confirmed or ruled out)

Программа: **{program_name}** ({platform}) — {program_url}
Team: `{team_handle}`

## Контекст (scope + recon)
{prior_context}

## Shopify playbook (if applicable)
{shopify_playbook}

## Задача
Протестируй **минимум 3 гипотезы** из recon. Для каждой: команда → результат.

Допустимо: IDOR, XSS (reflected/stored), SSRF, misconfig, logic bugs, open redirects, CORS, auth bypass на **своих** тест-аккаунтах.

Запрещено: DoS, brute-force, spam, destructive tests, чужие данные.

## Для каждой гипотезы
1. Asset + technique
2. Exact curl/HTTP request (copy-paste ready)
3. Response snippet (status, relevant body)
4. Verdict: **confirmed** | **not confirmed** | **needs auth**

## Формат ответа

**Research log (RU):** все гипотезы с командами и выводами.

```json
{{
  "phase": "hunt",
  "hypotheses_tested": 3,
  "results": [
    {{
      "hypothesis": "...",
      "asset": "https://...",
      "verdict": "confirmed|not_confirmed|blocked",
      "evidence_commands": ["curl -i '...'"],
      "evidence_snippet": "..."
    }}
  ],
  "best_candidate": {{
    "has_finding": true,
    "title": "...",
    "severity": "medium",
    "weakness_type": "...",
    "asset": "https://...",
    "impact": "EN 2+ sentences",
    "reproduction_steps": "1. ...\\n2. ...\\n3. ..."
  }},
  "notes": "итог для report-фазы"
}}
```

Если `has_finding: false` — всё равно документируй что тестировал. **confirmed** только с реальным PoC.
