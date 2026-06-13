"""Server health metrics and site checks."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass

import httpx
import psutil

from orchestrator.config import PUBLIC_SITE_URL, SITE_LOCAL_HOST, SITE_URL
from orchestrator.format_ru import format_load, format_percent


@dataclass
class HealthSnapshot:
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    load_avg: tuple[float, float, float]
    site_ok: bool
    docker_ok: bool
    degraded: bool
    light_mode: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _docker_ok() -> bool:
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--status", "running"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return result.returncode == 0 and "site" in result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return False


def _site_check_urls() -> list[tuple[str, dict[str, str] | None]]:
    """URLs to probe, in priority order. Local Caddy needs Host header."""
    candidates: list[tuple[str, dict[str, str] | None]] = []
    seen: set[str] = set()

    for base in (PUBLIC_SITE_URL, SITE_URL):
        base = base.rstrip("/")
        if not base or base in ("http://localhost", "https://localhost"):
            continue
        url = f"{base}/resume"
        if url not in seen:
            seen.add(url)
            candidates.append((url, None))

    local = (f"http://127.0.0.1/resume", {"Host": SITE_LOCAL_HOST})
    if local[0] not in seen:
        candidates.append(local)

    return candidates


def _site_ok() -> bool:
    for url, headers in _site_check_urls():
        try:
            resp = httpx.get(
                url,
                timeout=10,
                follow_redirects=True,
                headers=headers or {},
            )
            if resp.status_code < 500:
                return True
        except httpx.HTTPError:
            continue
    return False


def collect_health() -> HealthSnapshot:
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.5)
    load = psutil.getloadavg()
    site_ok = _site_ok()
    docker_ok = _docker_ok()
    mem_avail_mb = mem.available / (1024 * 1024)

    degraded = (
        cpu > 85
        or mem.percent > 85
        or disk.used / disk.total > 0.9
        or not site_ok
    )
    light_mode = cpu > 85 or mem_avail_mb < 512

    return HealthSnapshot(
        cpu_percent=round(cpu, 1),
        memory_percent=round(mem.percent, 1),
        memory_available_mb=round(mem_avail_mb, 1),
        disk_percent=round(disk.used / disk.total * 100, 1),
        load_avg=load,
        site_ok=site_ok,
        docker_ok=docker_ok,
        degraded=degraded,
        light_mode=light_mode,
    )


def format_health(h: HealthSnapshot) -> str:
    return (
        f"CPU: {format_percent(h.cpu_percent)} | RAM: {format_percent(h.memory_percent)} "
        f"({h.memory_available_mb:.0f} MB свободно)\n"
        f"Диск: {format_percent(h.disk_percent)} | Load: {format_load(h.load_avg)}\n"
        f"Сайт: {'OK' if h.site_ok else 'ЛЕЖИТ'} | Docker: {'OK' if h.docker_ok else 'ПРОБЛЕМА'}\n"
        f"Режим: {'облегчённый' if h.light_mode else 'полный'}"
    )
