"""Resume sync orchestration — diff, auth check, push with user approve gate."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

from job_hunt.config import (
    JOBHUNT_RESUME_AUTO_SYNC,
    JOBHUNT_RESUME_SYNC_ENABLED,
)
from job_hunt.habr_profile import sync_habr_profile, verify_habr_auth
from job_hunt.hh_digest import format_hh_digest_markdown
from job_hunt.hh_resume import HH_DEPRECATED_MSG
from job_hunt.linkedin_profile import linkedin_sync_note, verify_linkedin_auth
from job_hunt.resume_source import ResumePayload, load_resume_payload
from orchestrator.state import kv_get, kv_set

logger = logging.getLogger(__name__)

KV_FINGERPRINT = "resume_sync_fingerprint"
KV_LAST_HH = "resume_sync_last_hh"
KV_LAST_HABR = "resume_sync_last_habr"

Platform = Literal["hh", "habr", "linkedin", "all"]


@dataclass(frozen=True)
class PlatformAuth:
    platform: str
    ok: bool
    message: str
    extra: str = ""


@dataclass(frozen=True)
class SyncPlan:
    payload: ResumePayload
    changed: bool
    hh_fields: tuple[str, ...]
    habr_fields: tuple[str, ...]
    linkedin_note: str


def auth_status_all() -> list[PlatformAuth]:
    if not JOBHUNT_RESUME_SYNC_ENABLED:
        return [
            PlatformAuth("sync", False, "JOBHUNT_RESUME_SYNC_ENABLED=false"),
        ]

    results: list[PlatformAuth] = []

    results.append(
        PlatformAuth(
            "hh",
            False,
            "digest only — " + HH_DEPRECATED_MSG,
            "use /jobs hh-digest",
        )
    )

    habr = verify_habr_auth()
    results.append(PlatformAuth("habr", habr.ok, habr.message, habr.profile_url))

    li = verify_linkedin_auth()
    results.append(PlatformAuth("linkedin", li.ok, li.message))

    return results


def build_sync_plan() -> SyncPlan:
    payload = load_resume_payload()
    last_fp = kv_get(KV_FINGERPRINT, "")
    changed = payload.fingerprint != last_fp

    return SyncPlan(
        payload=payload,
        changed=changed,
        hh_fields=("title", "about", "skills"),  # manual paste via digest
        habr_fields=("about", "skills", "title"),
        linkedin_note=linkedin_sync_note(pdf_url="https://mpeshekhonov.ru/ru/resume/download"),
    )


def format_auth_markdown() -> str:
    lines = ["# Resume sync — авторизации", ""]
    for row in auth_status_all():
        mark = "✅" if row.ok else "❌"
        lines.append(f"- {mark} **{row.platform}** — {row.message}")
        if row.extra:
            lines.append(f"  _{row.extra}_")
    lines.extend(
        [
            "",
            "Источник: `site/content/resume/resume.json`",
            "",
            "`/jobs sync` — diff · `/jobs hh-digest` — текст для HH (ручная вставка)",
            "",
            "Setup: `docs/JOB-HUNT-AUTH-SETUP.md`",
        ]
    )
    return "\n".join(lines)


def format_sync_plan_markdown() -> str:
    plan = build_sync_plan()
    lines = [
        "# Resume sync — план",
        "",
        f"**Fingerprint:** `{plan.payload.fingerprint}`",
        f"**Изменилось с прошлого sync:** {'да' if plan.changed else 'нет'}",
        "",
        f"**Title:** {plan.payload.title}",
        f"**Skills:** {len(plan.payload.skills)} шт.",
        "",
    ]

    if plan.hh_fields:
        lines.append(
            f"**HH (ручное):** поля {', '.join(plan.hh_fields)} — `/jobs hh-digest`"
        )
    else:
        lines.append("**HH:** `/jobs hh-digest`")

    lines.append(f"**Habr:** {', '.join(plan.habr_fields)} (JH-14 Playwright)")
    lines.append(f"**LinkedIn:** {plan.linkedin_note}")
    lines.extend(
        [
            "",
            "Push:",
            "- `/approve resume habr` — после JH-14",
            "- `/approve resume all` — habr + linkedin reminder",
            "",
            "_HH API закрыт 15.12.2025 — auto-push через OAuth невозможен_",
        ]
    )
    if JOBHUNT_RESUME_AUTO_SYNC:
        lines.append("")
        lines.append("_AUTO_SYNC включён — daily может push без approve (не рекомендуется)_")
    return "\n".join(lines)


def apply_sync(platform: Platform) -> dict[str, Any]:
    if not JOBHUNT_RESUME_SYNC_ENABLED:
        return {"ok": False, "message": "Resume sync disabled"}

    payload = load_resume_payload()
    results: dict[str, Any] = {"ok": True, "platforms": {}}

    targets: tuple[str, ...]
    if platform == "all":
        targets = ("hh", "habr", "linkedin")
    else:
        targets = (platform,)

    for name in targets:
        if name == "hh":
            results["platforms"]["hh"] = _apply_hh_digest(payload)
        elif name == "habr":
            results["platforms"]["habr"] = _apply_habr(payload)
        elif name == "linkedin":
            results["platforms"]["linkedin"] = {
                "ok": True,
                "message": linkedin_sync_note(
                    pdf_url="https://mpeshekhonov.ru/ru/resume/download"
                ),
            }

    platforms = results["platforms"]
    if "hh" in platforms and len(platforms) == 1:
        results["ok"] = bool(platforms["hh"].get("ok"))
    elif "hh" in platforms:
        # HH digest is informational; overall ok if habr/linkedin succeed when present
        non_hh = {k: v for k, v in platforms.items() if k != "hh"}
        results["ok"] = all(p.get("ok") for p in non_hh.values()) if non_hh else True
    elif platforms:
        results["ok"] = any(p.get("ok") for p in platforms.values())
    else:
        results["ok"] = False

    if results["ok"] and "habr" in platforms and platforms["habr"].get("ok"):
        kv_set(KV_FINGERPRINT, payload.fingerprint)
    return results


def _apply_hh_digest(payload) -> dict[str, Any]:
    digest = format_hh_digest_markdown(payload)
    return {
        "ok": True,
        "message": HH_DEPRECATED_MSG,
        "digest": digest,
        "manual": True,
    }


def _apply_habr(payload) -> dict[str, Any]:
    ok, msg = sync_habr_profile(
        about_text=payload.about_text,
        skills=list(payload.skills),
    )
    if ok:
        kv_set(KV_LAST_HABR, payload.fingerprint)
    return {"ok": ok, "message": msg}
