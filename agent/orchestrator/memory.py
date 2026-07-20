"""Build context pack and persist daily memory."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from orchestrator.config import MEMORY_DIR, TASKS_DIR
from orchestrator.health import HealthSnapshot


def _read(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars]


def _recent_daily_logs(limit: int = 3) -> str:
    daily_dir = MEMORY_DIR / "daily"
    if not daily_dir.exists():
        return ""
    files = sorted(daily_dir.glob("*.md"), reverse=True)[:limit]
    parts = []
    for f in files:
        parts.append(f"### {f.name}\n{_read(f, 2000)}")
    return "\n\n".join(parts)


def build_context_pack(health: HealthSnapshot) -> str:
    index = _read(MEMORY_DIR / "INDEX.md", 3000)
    goals = _read(MEMORY_DIR / "goals.md", 2500)
    career_notes = _read(MEMORY_DIR / "career-copy-notes.md", 2500)
    job_backlog = _read(TASKS_DIR / "job_hunt_backlog.md", 3000)
    career_system = _read(
        MEMORY_DIR.parent.parent / "docs" / "career-growth-system.md", 2500
    )
    instructions = _read(MEMORY_DIR.parent / "instructions.md", 2000)
    backlog = _read(TASKS_DIR / "site_backlog.md", 1500)
    daily = _recent_daily_logs(3)
    template = _read(TASKS_DIR / "daily_prompt.md", 5000)
    hr_flags = _read(MEMORY_DIR / "lessons" / "resume_no_hr_red_flags.md", 1500)

    return f"""# Контекст daily-агента (career hunter)

## Здоровье сервера
- CPU: {health.cpu_percent}%
- RAM: {health.memory_percent}% ({health.memory_available_mb} MB свободно)
- Сайт OK: {health.site_ok}
- Облегчённый режим: {health.light_mode}

## Harness map
{instructions}

## INDEX
{index}

## Цели
{goals}

## Career copy notes
{career_notes}

## Job hunt backlog
{job_backlog}

## Career strategy (excerpt)
{career_system}

## HR red flags (resume)
{hr_flags}

## Бэклог сайта (только emergency)
{backlog}

## Недавние daily-логи
{daily}

## Шаблон задачи
{template}
"""


def ensure_daily_log() -> Path:
    daily_dir = MEMORY_DIR / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = daily_dir / f"{today}.md"
    if not path.exists():
        path.write_text(
            f"# Daily Log {today}\n\n"
            "## План\n\n## Итог\n\n## Сайт\n\n"
            "## Поиск работы\n\n## Источники\n\n## Уроки\n\n",
            encoding="utf-8",
        )
    return path


def get_latest_daily_log() -> str:
    daily_dir = MEMORY_DIR / "daily"
    if not daily_dir.exists():
        return ""
    files = sorted(daily_dir.glob("*.md"), reverse=True)
    if not files:
        return ""
    return files[0].read_text(encoding="utf-8").strip()


def append_daily_section(section: str, content: str) -> None:
    path = ensure_daily_log()
    text = path.read_text(encoding="utf-8")
    marker = f"## {section}"
    if marker in text:
        text = text.replace(marker, f"{marker}\n\n{content}\n", 1)
    else:
        text += f"\n\n{marker}\n\n{content}\n"
    path.write_text(text, encoding="utf-8")
