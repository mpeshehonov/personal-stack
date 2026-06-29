"""HH.ru resume digest for manual paste — applicant API closed 2025-12-15."""

from __future__ import annotations

from job_hunt.resume_source import ResumePayload, hh_description, load_resume_payload

HH_API_CLOSED_NOTE = (
    "API соискателя HH закрыт с 15.12.2025. "
    "Авто-push через OAuth недоступен. Используй digest или JH-16 (Playwright + cookie)."
)


def format_hh_digest_markdown(payload: ResumePayload | None = None) -> str:
    payload = payload or load_resume_payload()
    skills_line = ", ".join(payload.skills[:30])
    if len(payload.skills) > 30:
        skills_line += f" (+{len(payload.skills) - 30})"

    return "\n".join(
        [
            "# HH.ru — ручное обновление (digest)",
            "",
            f"_{HH_API_CLOSED_NOTE}_",
            "",
            "## Должность",
            payload.title,
            "",
            "## О себе",
            hh_description(payload),
            "",
            "## Ключевые навыки",
            skills_line,
            "",
            "## Действия вручную",
            "1. https://hh.ru/applicant/resumes",
            "2. Открыть резюме → редактировать поля выше",
            "3. «Поднять в поиске» — кнопка в UI",
            "",
            f"_Fingerprint site: `{payload.fingerprint}`_",
        ]
    )
