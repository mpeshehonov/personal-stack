"""Azuro Protocol client — read-only market fetch + order stub."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from finance.venue_base import TradeVenue
from orchestrator.config import load_env_file

logger = logging.getLogger(__name__)

AZURO_API_BASE = "https://api.onchainfeed.org/api/v1/public"


class AzuroClient(TradeVenue):
    """Azuro Backend API (V3). Public market-manager endpoints need no auth."""

    def __init__(self) -> None:
        load_env_file(".env.finance")
        self.api_base = os.environ.get("AZURO_API_BASE", AZURO_API_BASE).rstrip("/")
        self.environment = os.environ.get("AZURO_ENVIRONMENT", "PolygonUSDT")

    @property
    def name(self) -> str:
        return "azuro"

    def get_markets(self, limit: int = 20) -> list[dict[str, Any]]:
        per_page = max(10, min(limit, 50))
        try:
            resp = httpx.get(
                f"{self.api_base}/market-manager/games-by-filters",
                params={
                    "environment": self.environment,
                    "gameState": "Prematch",
                    "orderBy": "startsAt",
                    "orderDirection": "asc",
                    "page": 1,
                    "perPage": per_page,
                },
                timeout=30,
            )
            resp.raise_for_status()
            games = resp.json().get("games", [])
        except httpx.HTTPError as e:
            logger.warning("Azuro games fetch failed: %s", e)
            return []

        markets: list[dict[str, Any]] = []
        for g in games[:limit]:
            market_id = str(g.get("gameId") or g.get("id") or "")
            if not market_id:
                continue
            markets.append(
                self.normalize_market(
                    {
                        "id": market_id,
                        "condition_id": market_id,
                        "title": g.get("title", ""),
                        "slug": g.get("slug", ""),
                        "starts_at": g.get("startsAt"),
                        "sport": (g.get("sport") or {}).get("name"),
                        "league": (g.get("league") or {}).get("name"),
                        "turnover": g.get("turnover"),
                    }
                )
            )
        return markets

    def place_order(self, market_id: str, side: str, size_usd: float) -> dict[str, Any]:
        """
        Live orders: POST /bet/orders/ordinar with wallet signature.
        See https://gem.azuro.org/hub/apps/APIs/backend
        """
        load_env_file(".env.finance")
        if not os.environ.get("OPERATIONAL_WALLET_PRIVATE_KEY"):
            return {
                "status": "skipped",
                "venue": self.name,
                "reason": "no operational wallet configured",
            }
        return {
            "status": "stub",
            "venue": self.name,
            "market_id": market_id,
            "side": side,
            "size_usd": size_usd,
            "note": "Wire Azuro bet/orders/ordinar + SIWE for live orders",
        }

    def check_health(self) -> dict[str, Any]:
        try:
            resp = httpx.get(
                f"{self.api_base}/market-manager/navigation",
                params={"environment": self.environment},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            sports = data if isinstance(data, list) else data.get("sports", data)
            ok = bool(sports)
            return {"venue": self.name, "ok": ok, "detail": "navigation reachable"}
        except httpx.HTTPError as e:
            logger.warning("Azuro health check failed: %s", e)
            return {"venue": self.name, "ok": False, "detail": str(e)}
