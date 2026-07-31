# Opportunity OS Multi-Vertical Design (2026-07-31)

## Goal

Expand Opportunity OS beyond JOB so `/brief` surfaces **actions that stabilize income**, not only vacancies.

Order: **CLIENT → NETWORK → PRODUCT** (incl. net-new product ideas).

## Non-goals (v1)

- Full Company/Person CRM from `career-opportunities-schema.md`
- Scraping Upwork/FL.ru at scale (optional later)
- Claiming employer/client IP as resellable products

## Verticals

### 1. CLIENT (first)

**Signals (deterministic generators, no LLM required):**

- Contract / retainer bridges from profile (`contract_ok`, income gap)
- Outreach targets typed as CLIENT opportunities (entity = company or “open market”)
- Optional: seed list from `opportunity_profile.json` → `client_targets[]`

**Scoring:** reuse Stage B weights; boost `income` + `urgency` when RED / no interviews.

**Next actions:** `WRITE_TO_CONTACT`, `REVIEW`, `APPLY` (as “отправить оффер/сообщение”).

### 2. NETWORK

**Signals:**

- Warm intros from profile `network_contacts[]` (name, channel, relation, last_touch)
- “Ask 1 human this week” standing opportunity if contacts empty → prompt user to add via `/profile` or memory file

**Next actions:** `WRITE_TO_CONTACT`, `FOLLOW_UP`.

### 3. PRODUCT

Two lanes:

**A. Package & resell (owned IP only)**  
Only assets listed in profile `owned_product_assets[]` with `can_resell: true`.  
Never auto-derive from site `/projects` employer case studies (X5, Citilink, sendonate, PREEGLOS, etc.).

**B. Net-new product opportunities**  
Generator proposes *new* product theses from gaps/skills/market angles (POS tablets, seat-map SaaS lite, streamer tools clone-avoidant niches) as `PRODUCT` with `analysis.kind = net_new`.  
Human must approve before any build.

## Brief UX

`/brief` sections:

1. Follow-ups (JOB applied silence) — keep  
2. Today JOB  
3. **CLIENT** (up to 2)  
4. **NETWORK** (up to 2)  
5. **PRODUCT** (up to 2: owned package and/or net-new)  
6. Funnel by type (optional compact line)

Buttons: reuse like/pass where `job_lead_id` null → opportunity-id callbacks `o:like:{id}`.

## Profile additions

```json
"client_targets": [],
"network_contacts": [],
"owned_product_assets": [
  {"key": "...", "title": "...", "can_resell": true, "notes": "..."}
],
"product_ideas_blocked": ["do not clone sendonate", "..."]
```

## Daily agent

After scan: `ensure_vertical_opportunities()` upserts CLIENT/NETWORK/PRODUCT rows (idempotent by `source` key).

## Success criteria

- `/brief` shows non-JOB actions with Russian copy  
- No employer portfolio item becomes a PRODUCT without `owned_product_assets`  
- Net-new ideas appear weekly even if owned list empty  
- Tests for generators + brief sections  

## Open question (user)

Which personal assets may be packaged/resold? Candidates to confirm: SmartFish KKM, SmartPrice, ZodiacLab bots, personal-stack itself — **not** X5/BI.ZONE/NLMK/Citilink/POTALONU client work.
