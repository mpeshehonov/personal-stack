# Career Opportunities Schema

**Status:** design (not implemented)  
**Related:** `docs/career-growth-system.md`, `docs/career-growth-backlog.md`  
**Storage target:** extend `agent/state.sqlite` (same pattern as `job_leads`)  
**Rule:** every claim about a company/person should link to `Evidence`; never invent facts.

---

## Entity relationship overview

```text
Company 1──* Person
Company 1──* Opportunity
Company 1──* Evidence
Person  1──* Contact
Person  1──* Evidence
Opportunity *──* Person          (hiring managers / recruiters)
Opportunity 1──* Application     (optional; vacancy-bound)
Opportunity 1──* Outreach
Contact 1──* Outreach
Outreach *──* Evidence           (why this angle)
ResumeVersion *──* Application
ResumeVersion *──* Outreach      (which version was used)
Relationship (Person ↔ you)      # warmth / history
ResearchTask → Company | Person | Opportunity
```

Legacy `job_leads` / `job_applications` remain during migration: a `job_lead` may **link** to `Company` + `Opportunity` via `external_ref`.

---

## 1. Company

Canonical org we may want to work with (employer or client).

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `created_at` / `updated_at` | datetime | |
| `company_name` | text | Display name |
| `domain` | text | Normalized apex domain (unique if present) |
| `website` | text | |
| `linkedin_url` | text | |
| `github_url` | text | Org URL |
| `twitter_or_x_url` | text | |
| `telegram_url` | text | |
| `industry` | text | |
| `product_description` | text | Short, sourced |
| `geography` | text | Markets / HQ narrative |
| `legal_entity_location` | text | If known |
| `remote_policy` | enum | `unknown\|onsite\|hybrid\|remote\|remote_ok` |
| `estimated_company_size` | text | e.g. `51-200` |
| `estimated_engineering_size` | text | |
| `founders_json` | JSON | Light list; details in Person |
| `cto_person_id` | FK? | Optional quick link |
| `engineering_managers_json` | JSON | IDs or names pending Person rows |
| `known_russian_or_cis_connections` | text | Summary |
| `known_employees_from_russia_or_cis_json` | JSON | |
| `evidence_of_hiring_from_russia_or_cis` | text | Summary + evidence IDs |
| `current_open_roles_json` | JSON | Snapshot of known openings |
| `tech_stack_json` | JSON | |
| `funding_or_business_signals` | text | |
| `score` | int | 0–100 |
| `score_breakdown_json` | JSON | factor → {points, evidence_ids} |
| `confidence` | float | 0–1 |
| `source_urls_json` | JSON | |
| `last_checked_at` | datetime | |
| `status` | enum | `seed\|researching\|candidate\|shortlist\|approved\|outreach\|paused\|rejected\|hired_or_client\|archive` |
| `next_action` | text | Human-readable |
| `next_action_at` | datetime | |
| `notes` | text | |

**Indexes:** `domain` UNIQUE NULLS DISTINCT; `status`; `score DESC`.

---

## 2. Person

Decision maker or relevant employee.

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `company_id` | FK Company | Nullable if independent recruiter |
| `full_name` | text | |
| `role_title` | text | Current |
| `role_category` | enum | `founder\|cto\|vp_eng\|eng_manager\|recruiter\|other` |
| `linkedin_url` | text | |
| `github_url` | text | |
| `twitter_or_x_url` | text | |
| `telegram_url` | text | |
| `location` | text | |
| `background_summary` | text | Sourced only |
| `russian_or_cis_background` | bool/unknown | |
| `relevance_score` | int | 0–100 |
| `relevance_reasons_json` | JSON | |
| `source_urls_json` | JSON | |
| `last_checked_at` | datetime | |
| `status` | enum | `discovered\|researched\|approved\|contacted\|replied\|closed` |
| `notes` | text | |

---

## 3. Opportunity

A concrete path to money: open role, hidden hiring thesis, or freelance need.

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `company_id` | FK | |
| `kind` | enum | `open_role\|hidden_hiring\|contract\|product_idea\|inbound` |
| `title` | text | |
| `description` | text | |
| `url` | text | Vacancy URL if any |
| `compensation_hint` | text | Never invent numbers |
| `remote_ok` | bool/unknown | |
| `fit_score` | int | Vs your profile |
| `fit_reasons_json` | JSON | |
| `status` | enum | `new\|shortlist\|outreach\|conversation\|interview\|offer\|won\|lost\|paused` |
| `job_lead_id` | FK? | Bridge to legacy `job_leads` |
| `resume_version_id` | FK? | Intended version |
| `next_action` | text | |
| `value_estimate_rub_month` | int? | Optional, user-set |
| `created_at` / `updated_at` | datetime | |

---

## 4. Evidence

Atomic sourced fact. Prevents hallucinated CIS/funding claims.

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `entity_type` | enum | `company\|person\|opportunity` |
| `entity_id` | int | |
| `claim` | text | Short statement |
| `source_url` | text | Required when external |
| `source_type` | enum | `website\|linkedin\|github\|job_board\|telegram\|news\|manual\|other` |
| `observed_at` | datetime | |
| `confidence` | float | |
| `raw_excerpt` | text | Optional quote |

---

## 5. Contact

How to reach a Person (channel instance).

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `person_id` | FK | |
| `channel` | enum | `email\|linkedin\|telegram\|other` |
| `value` | text | Address / URL (secret-careful) |
| `verified` | bool | |
| `is_primary` | bool | |
| `source` | text | How obtained |
| `created_at` | datetime | |

---

## 6. Outreach

One touch (message attempt).

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `opportunity_id` | FK? | |
| `person_id` | FK | |
| `contact_id` | FK? | |
| `resume_version_id` | FK? | |
| `channel` | enum | |
| `subject` | text | |
| `body` | text | Draft or sent copy |
| `angle` | text | Hook summary |
| `status` | enum | `draft\|awaiting_approve\|approved\|sent\|replied\|bounced\|closed` |
| `approved_at` | datetime | |
| `sent_at` | datetime | |
| `follow_up_at` | datetime | |
| `response_summary` | text | |
| `created_at` | datetime | |

**Invariant:** transition to `sent` only after explicit user approve (Telegram `/approve outreach <id>`).

---

## 7. ResumeVersion

Targeted packaging of the master profile.

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `code` | text | `A_frontend_product`, `B_fullstack`, `C_ai_augmented`, `D_founding` |
| `label` | text | |
| `summary` | text | |
| `highlights_json` | JSON | Selected bullets / projects |
| `site_path` | text | Optional export path |
| `is_default` | bool | |
| `updated_at` | datetime | |

Master content remains in `site/content/resume/` + `resume-data.ts`; versions are overlays.

---

## 8. Application

Vacancy-bound application (extends today’s `job_applications`).

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | Prefer migrate existing table |
| `opportunity_id` | FK? | New link |
| `job_lead_id` | FK | Legacy |
| `resume_version_id` | FK? | |
| `cover_letter` | text | |
| `status` | enum | `draft\|ready\|submitted\|viewed\|rejected\|interview\|offer` |
| `submitted_at` | datetime | |
| `notes` | text | |

---

## 9. Relationship

Your relationship state with a Person (warmth).

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `person_id` | FK UNIQUE | |
| `warmth` | enum | `cold\|warm\|hot\|do_not_contact` |
| `how_we_know` | text | |
| `last_interaction_at` | datetime | |
| `notes` | text | |

---

## 10. ResearchTask

Work queue for Level 1–2 automation.

| Field | Type | Notes |
|-------|------|-------|
| `id` | PK | |
| `kind` | enum | `enrich_company\|find_people\|score\|brief\|find_contacts\|monitor` |
| `entity_type` | enum | `company\|person\|opportunity` |
| `entity_id` | int | |
| `priority` | int | |
| `status` | enum | `queued\|running\|done\|failed` |
| `result_summary` | text | |
| `error` | text | |
| `created_at` / `finished_at` | datetime | |

Can map to existing `task_queue` or sit beside it.

---

## Status machines (simplified)

### Company
`seed → researching → candidate → shortlist → approved → outreach → (paused|rejected|hired_or_client|archive)`

### Opportunity
`new → shortlist → outreach → conversation → interview → offer → won|lost`

### Outreach
`draft → awaiting_approve → approved → sent → replied|bounced|closed`

---

## Scoring breakdown JSON (example)

```json
{
  "total": 78,
  "factors": {
    "cis_connection": {"points": 18, "max": 20, "evidence_ids": [12, 15]},
    "hire_from_russia": {"points": 12, "max": 15, "evidence_ids": [16]},
    "remote": {"points": 12, "max": 15, "evidence_ids": [17]},
    "tech_fit": {"points": 14, "max": 15, "evidence_ids": [18]},
    "comp_potential": {"points": 6, "max": 10, "evidence_ids": []},
    "quality": {"points": 8, "max": 10, "evidence_ids": [19]},
    "hidden_hiring": {"points": 6, "max": 10, "evidence_ids": [20]},
    "case_relevance": {"points": 2, "max": 5, "evidence_ids": [21]}
  },
  "explanation": "CIS hiring culture signals + remote OK + React domain UI; no public FE role but eng growth."
}
```

---

## Telegram command mapping (proposed)

| Command | Entity effect |
|---------|----------------|
| `/companies` | List shortlist |
| `/company <id>` | Show score + evidence |
| `/brief <company_id>` | Generate/show research brief |
| `/people <company_id>` | List persons |
| `/approve company <id>` | status → approved |
| `/approve contact <id>` | person ready |
| `/approve outreach <id>` | allow send |
| `/reject company <id>` | archive |
| `/cover <lead_id>` | Keep legacy vacancy path |
| `/jobs` | Keep as vacancy feed → optional company seed |

---

## Migration notes

1. Add tables without dropping `job_leads` / `job_applications`.  
2. Backfill `Company` from distinct `job_leads.company` + URL host where possible.  
3. Link new opportunities to old leads via `job_lead_id`.  
4. Secrets (emails) stay in DB with restricted bot display (mask).  
5. No PII in git — only SQLite on server + memory summaries without secrets.
