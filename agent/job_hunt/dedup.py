"""Cross-source vacancy deduplication helpers."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """Normalize URL for duplicate checks."""
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urlparse(url.lower())
    host = parsed.netloc.removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


def vacancy_fingerprint(vacancy: dict[str, Any]) -> str:
    """Stable key from title + company (cross-source duplicate signal)."""
    employer = vacancy.get("employer") or {}
    title = re.sub(r"\s+", " ", (vacancy.get("name") or "").lower()).strip()
    company = re.sub(r"\s+", " ", (employer.get("name") or "").lower()).strip()
    if not title:
        return ""
    return f"{title}|{company}" if company else title


def is_cross_source_duplicate(
    vacancy: dict[str, Any],
    *,
    seen_urls: set[str],
    seen_fingerprints: set[str],
) -> bool:
    """True if vacancy duplicates another source in the current batch."""
    url_key = normalize_url(vacancy.get("alternate_url") or "")
    fp = vacancy_fingerprint(vacancy)
    if url_key and url_key in seen_urls:
        return True
    if fp and len(fp) >= 8 and fp in seen_fingerprints:
        return True
    return False


def register_vacancy_keys(
    vacancy: dict[str, Any],
    *,
    seen_urls: set[str],
    seen_fingerprints: set[str],
) -> None:
    url_key = normalize_url(vacancy.get("alternate_url") or "")
    fp = vacancy_fingerprint(vacancy)
    if url_key:
        seen_urls.add(url_key)
    if fp and len(fp) >= 8:
        seen_fingerprints.add(fp)


def dedupe_vacancies(vacancies: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Remove duplicates within a fetched batch (URL + title/company fingerprint)."""
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()
    unique: list[dict[str, Any]] = []
    skipped = 0
    for vacancy in vacancies:
        if is_cross_source_duplicate(vacancy, seen_urls=seen_urls, seen_fingerprints=seen_fingerprints):
            skipped += 1
            continue
        register_vacancy_keys(vacancy, seen_urls=seen_urls, seen_fingerprints=seen_fingerprints)
        unique.append(vacancy)
    return unique, skipped
