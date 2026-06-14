"""Validate daily log structure after agent run."""

from __future__ import annotations

import re
from pathlib import Path

from orchestrator.config import MEMORY_DIR

_REQUIRED_SECTIONS = ("План", "Итог", "Сайт", "Финансы", "Баг-баунти", "Уроки")
_SECTION_MARKER = re.compile(r"^## (.+)$", re.MULTILINE)
_MIN_CONTENT_CHARS = 40


def validate_daily_log(path: Path | None = None) -> tuple[bool, list[str]]:
    """Return (ok, warnings). Warnings are non-fatal quality gaps."""
    if path is None:
        daily_dir = MEMORY_DIR / "daily"
        if not daily_dir.exists():
            return False, ["daily log directory missing"]
        files = sorted(daily_dir.glob("*.md"), reverse=True)
        if not files:
            return False, ["no daily log file"]
        path = files[0]

    text = path.read_text(encoding="utf-8")
    found = set(_SECTION_MARKER.findall(text))
    warnings: list[str] = []

    for section in _REQUIRED_SECTIONS:
        if section not in found:
            warnings.append(f"missing section: ## {section}")

    for section in _REQUIRED_SECTIONS:
        if section not in found:
            continue
        block = _section_body(text, section)
        if len(block.strip()) < _MIN_CONTENT_CHARS:
            warnings.append(f"section ## {section} too short (< {_MIN_CONTENT_CHARS} chars)")

    ok = len(warnings) == 0
    return ok, warnings


def _section_body(text: str, section: str) -> str:
    marker = f"## {section}"
    start = text.find(marker)
    if start < 0:
        return ""
    start += len(marker)
    rest = text[start:]
    next_h2 = re.search(r"\n## ", rest)
    if next_h2:
        return rest[: next_h2.start()]
    return rest
