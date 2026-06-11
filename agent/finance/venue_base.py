"""Abstract trading venue interface and registry."""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from orchestrator.config import load_env_file

logger = logging.getLogger(__name__)


class TradeVenue(ABC):
    """Common interface for market scan + order placement across venues."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short venue identifier (e.g. polymarket, azuro)."""

    @abstractmethod
    def get_markets(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return normalized market dicts for scanning."""

    @abstractmethod
    def place_order(self, market_id: str, side: str, size_usd: float) -> dict[str, Any]:
        """Submit or stub an order; returns execution metadata."""

    @abstractmethod
    def check_health(self) -> dict[str, Any]:
        """Lightweight connectivity probe for orchestrator dashboards."""

    def normalize_market(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Attach venue tag so multi-venue scans stay distinguishable."""
        out = dict(raw)
        out.setdefault("venue", self.name)
        return out


class PolymarketVenue(TradeVenue):
    """Adapter wrapping the existing PolymarketClient."""

    def __init__(self) -> None:
        from finance.polymarket_client import PolymarketClient

        self._client = PolymarketClient()

    @property
    def name(self) -> str:
        return "polymarket"

    def get_markets(self, limit: int = 20) -> list[dict[str, Any]]:
        return [self.normalize_market(m) for m in self._client.get_markets(limit=limit)]

    def place_order(self, market_id: str, side: str, size_usd: float) -> dict[str, Any]:
        result = self._client.place_order(market_id, side, size_usd)
        result["venue"] = self.name
        return result

    def check_health(self) -> dict[str, Any]:
        markets = self._client.get_markets(limit=1)
        return {
            "venue": self.name,
            "ok": bool(markets),
            "detail": "fetched markets" if markets else "empty or unreachable",
        }


_VENUE_FACTORIES: dict[str, type[TradeVenue]] = {}


def _register_defaults() -> None:
    global _VENUE_FACTORIES
    if _VENUE_FACTORIES:
        return
    _VENUE_FACTORIES = {
        "polymarket": PolymarketVenue,
    }
    from finance.azuro_client import AzuroClient
    from finance.cex_client import CexClient

    _VENUE_FACTORIES["azuro"] = AzuroClient
    _VENUE_FACTORIES["cex"] = CexClient


def get_enabled_venues() -> list[TradeVenue]:
    """Instantiate venues listed in FINANCE_VENUES (default: polymarket)."""
    load_env_file(".env.finance")
    _register_defaults()
    raw = os.environ.get("FINANCE_VENUES", "polymarket")
    names = [n.strip().lower() for n in raw.split(",") if n.strip()]
    venues: list[TradeVenue] = []
    for name in names:
        factory = _VENUE_FACTORIES.get(name)
        if factory is None:
            logger.warning("Unknown FINANCE_VENUES entry: %s", name)
            continue
        venues.append(factory())
    return venues
