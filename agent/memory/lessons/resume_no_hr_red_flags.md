# Resume: no HR red flags (2026-07-20)

User feedback after Product Engineer pass: several lines were technically true but **read as slop / jargon / overshare** to recruiters.

## Failures that shipped

| Line | Why it fails | Fix pattern |
|------|----------------|-------------|
| `без выезда на место` | Sounds like a joke / excuse, not an achievement | State the tool outcome: Sentry sped up prod fixes |
| `FSD-клиент` | Architecture buzzword as product noun | Domain first: «сервис управления …»; FSD only in stack |
| `Retail/wholesale` | EN calque; unclear to RU HR | «розница и оптовый каталог» / retail and B2B |
| `в SOC` | Acronym without context for generalist HR | «аналитики киберугроз» / Threat Intelligence product |
| `ТК РФ / самозанятый / USDT. ASAP.` in hero | Negotiation rails + urgency dump in first scan | Goal = role only; rails offline; ASAP = badge only |

## Rule for agents

Before editing `resume-data.ts`, `resume.md`, `resume.json`, project taglines:

1. Run the **HR / recruiter red-flag pass** in `agent/skills/resume-copy/SKILL.md`.
2. Prefer a slightly plainer sentence over a clever insider one.
3. Payment form, crypto, employment type → `career-copy-notes` / negotiation, **never** public hero/summary unless user explicitly asks.

## Related

- `resume_sells_in_15_seconds.md` — packaging speed
- `agent/memory/career-copy-notes.md` — confirmed facts (may include rails for private use)
