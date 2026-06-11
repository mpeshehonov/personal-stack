"""Polymarket CLOB client (read + order placement stub)."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from orchestrator.config import load_env_file

logger = logging.getLogger(__name__)

CLOB_BASE = "https://clob.polymarket.com"
GEOBLOCK_URL = "https://polymarket.com/api/geoblock"


def is_geoblocked(data: dict[str, Any]) -> bool:
    """Return True when Polymarket geoblock API indicates trading is blocked."""
    if data.get("error"):
        return False
    return bool(
        data.get("blocked")
        or data.get("geoblocked")
        or data.get("is_blocked")
        or data.get("block")
    )


class PolymarketClient:
    def __init__(self) -> None:
        load_env_file(".env.finance")
        self.api_key = os.environ.get("POLYMARKET_API_KEY", "")
        self.rpc_url = os.environ.get("POLYGON_RPC_URL", "https://polygon-rpc.com")

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def check_geoblock(self) -> dict[str, Any]:
        try:
            resp = httpx.get(
                GEOBLOCK_URL,
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                return data
            return {"blocked": bool(data)}
        except httpx.HTTPError as e:
            logger.warning("Geoblock check failed: %s", e)
            return {"blocked": False, "error": str(e)}

    def get_markets(self, limit: int = 20) -> list[dict[str, Any]]:
        try:
            resp = httpx.get(
                f"{CLOB_BASE}/markets",
                params={"limit": limit},
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            return data.get("data", data.get("markets", []))
        except httpx.HTTPError as e:
            logger.warning("Polymarket fetch failed: %s", e)
            return []

    def place_order(self, market_id: str, side: str, size_usd: float) -> dict[str, Any]:
        """Live order placement — requires wallet integration."""
        geoblock = self.check_geoblock()
        if is_geoblocked(geoblock):
            return {
                "status": "blocked",
                "reason": "geoblocked",
                "geoblock": geoblock,
                "market_id": market_id,
                "side": side,
                "size_usd": size_usd,
            }

        load_env_file(".env.finance")
        private_key = os.environ.get("OPERATIONAL_WALLET_PRIVATE_KEY")
        if not private_key:
            return {"status": "skipped", "reason": "no operational wallet configured"}
        # Production: integrate py-clob-client or official SDK
        return {
            "status": "stub",
            "market_id": market_id,
            "side": side,
            "size_usd": size_usd,
            "note": "Wire py-clob-client for live orders",
        }
