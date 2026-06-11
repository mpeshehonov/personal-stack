"""Server health metrics and site checks."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass

import httpx
import psutil

from orchestrator.config import SITE_URL


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


def _site_ok() -> bool:
    for url in (f"{SITE_URL}/resume", "http://127.0.0.1:3000/resume"):
        try:
            resp = httpx.get(url, timeout=10, follow_redirects=True)
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
        cpu_percent=cpu,
        memory_percent=mem.percent,
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
        f"CPU: {h.cpu_percent}% | RAM: {h.memory_percent}% ({h.memory_available_mb} MB free)\n"
        f"Disk: {h.disk_percent}% | Load: {h.load_avg}\n"
        f"Site: {'OK' if h.site_ok else 'DOWN'} | Docker: {'OK' if h.docker_ok else 'ISSUE'}\n"
        f"Mode: {'light' if h.light_mode else 'full'}"
    )
