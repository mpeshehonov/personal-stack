"""Shopify Admin API tokens — static shpat_* or Dev Dashboard client credentials grant."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import httpx

from bounty.config import (
    SHOPIFY_APP_CLIENT_ID,
    SHOPIFY_APP_CLIENT_SECRET,
    SHOPIFY_SHOP1_ADMIN_TOKEN,
    SHOPIFY_SHOP1_DOMAIN,
    SHOPIFY_SHOP2_ADMIN_TOKEN,
    SHOPIFY_SHOP2_DOMAIN,
)
from orchestrator.config import SECRETS_DIR

logger = logging.getLogger(__name__)

_CACHE_PATH = SECRETS_DIR / ".shopify_token_cache.json"
_REFRESH_BUFFER_SEC = 300


def _load_cache() -> dict[str, Any]:
    if not _CACHE_PATH.exists():
        return {}
    try:
        return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(data: dict[str, Any]) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _exchange_client_credentials(domain: str, client_id: str, client_secret: str) -> dict[str, Any]:
    shop = domain.removeprefix("https://").removeprefix("http://").rstrip("/")
    url = f"https://{shop}/admin/oauth/access_token"
    resp = httpx.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Shopify token exchange failed ({resp.status_code}): {resp.text[:400]}")
    payload = resp.json()
    if not payload.get("access_token"):
        raise RuntimeError(f"Shopify token response missing access_token: {resp.text[:400]}")
    return payload


def get_admin_token(shop: int = 1) -> str:
    """Return Admin API access token for shop 1 or 2."""
    domain, static_token = (
        (SHOPIFY_SHOP1_DOMAIN, SHOPIFY_SHOP1_ADMIN_TOKEN)
        if shop == 1
        else (SHOPIFY_SHOP2_DOMAIN, SHOPIFY_SHOP2_ADMIN_TOKEN)
    )
    if not domain:
        raise RuntimeError(f"SHOPIFY_SHOP{shop}_DOMAIN not configured")
    if static_token:
        return static_token

    if not (SHOPIFY_APP_CLIENT_ID and SHOPIFY_APP_CLIENT_SECRET):
        raise RuntimeError(
            f"Shop {shop}: set SHOPIFY_SHOP{shop}_ADMIN_TOKEN or "
            "SHOPIFY_APP_CLIENT_ID + SHOPIFY_APP_CLIENT_SECRET"
        )

    cache = _load_cache()
    entry = cache.get(domain) or {}
    expires_at = float(entry.get("expires_at", 0))
    if entry.get("access_token") and time.time() < expires_at - _REFRESH_BUFFER_SEC:
        return str(entry["access_token"])

    payload = _exchange_client_credentials(
        domain, SHOPIFY_APP_CLIENT_ID, SHOPIFY_APP_CLIENT_SECRET
    )
    expires_in = int(payload.get("expires_in", 86399))
    cache[domain] = {
        "access_token": payload["access_token"],
        "scope": payload.get("scope", ""),
        "expires_at": time.time() + expires_in,
    }
    _save_cache(cache)
    logger.info("Shopify token refreshed for %s (expires_in=%s)", domain, expires_in)
    return str(payload["access_token"])


def shop_has_auth(shop: int = 1) -> bool:
    domain, static = (
        (SHOPIFY_SHOP1_DOMAIN, SHOPIFY_SHOP1_ADMIN_TOKEN)
        if shop == 1
        else (SHOPIFY_SHOP2_DOMAIN, SHOPIFY_SHOP2_ADMIN_TOKEN)
    )
    if not domain:
        return False
    if static:
        return True
    return bool(SHOPIFY_APP_CLIENT_ID and SHOPIFY_APP_CLIENT_SECRET)
