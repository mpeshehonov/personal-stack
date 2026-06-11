"""CEX client stub — Bybit NL / OKX public tickers (no keys for read)."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from finance.venue_base import TradeVenue
from orchestrator.config import load_env_file

logger = logging.getLogger(__name__)

DEFAULT_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")


class CexClient(TradeVenue):
    """
    Aggregates public spot tickers from Bybit NL and OKX.
    Trading requires API keys (BYBIT_* / OKX_*) after KYC.
    """

    def __init__(self) -> None:
        load_env_file(".env.finance")
        self.bybit_base = os.environ.get("BYBIT_API_BASE", "https://api.bybit.nl").rstrip("/")
        self.okx_base = os.environ.get("OKX_API_BASE", "https://www.okx.com").rstrip("/")
        symbols_raw = os.environ.get("CEX_SCAN_SYMBOLS", ",".join(DEFAULT_SYMBOLS))
        self.symbols = [s.strip() for s in symbols_raw.split(",") if s.strip()]

    @property
    def name(self) -> str:
        return "cex"

    def get_markets(self, limit: int = 20) -> list[dict[str, Any]]:
        """Expose tickers as pseudo-markets for multi-venue scanning."""
        markets: list[dict[str, Any]] = []
        for symbol in self.symbols:
            if len(markets) >= limit:
                break
            bybit = self._fetch_bybit_ticker(symbol)
            okx = self._fetch_okx_ticker(symbol)
            if not bybit and not okx:
                continue
            markets.append(
                self.normalize_market(
                    {
                        "id": symbol,
                        "condition_id": symbol,
                        "title": f"{symbol} spot (CEX)",
                        "bybit": bybit,
                        "okx": okx,
                        "last_price": (bybit or okx or {}).get("last"),
                    }
                )
            )
        return markets[:limit]

    def _fetch_bybit_ticker(self, symbol: str) -> dict[str, Any] | None:
        try:
            resp = httpx.get(
                f"{self.bybit_base}/v5/market/tickers",
                params={"category": "spot", "symbol": symbol},
                timeout=15,
            )
            resp.raise_for_status()
            items = (resp.json().get("result") or {}).get("list") or []
            if not items:
                return None
            t = items[0]
            return {
                "exchange": "bybit",
                "symbol": symbol,
                "last": t.get("lastPrice"),
                "bid": t.get("bid1Price"),
                "ask": t.get("ask1Price"),
                "change_24h_pct": t.get("price24hPcnt"),
            }
        except httpx.HTTPError as e:
            logger.warning("Bybit ticker %s failed: %s", symbol, e)
            return None

    def _fetch_okx_ticker(self, symbol: str) -> dict[str, Any] | None:
        inst_id = symbol.replace("USDT", "-USDT") if "-" not in symbol else symbol
        try:
            resp = httpx.get(
                f"{self.okx_base}/api/v5/market/ticker",
                params={"instId": inst_id},
                timeout=15,
            )
            resp.raise_for_status()
            items = resp.json().get("data") or []
            if not items:
                return None
            t = items[0]
            open_24h = float(t.get("open24h") or 0)
            last = float(t.get("last") or 0)
            change_pct = ((last - open_24h) / open_24h) if open_24h else None
            return {
                "exchange": "okx",
                "symbol": inst_id,
                "last": t.get("last"),
                "bid": t.get("bidPx"),
                "ask": t.get("askPx"),
                "change_24h_pct": change_pct,
            }
        except httpx.HTTPError as e:
            logger.warning("OKX ticker %s failed: %s", inst_id, e)
            return None

    def place_order(self, market_id: str, side: str, size_usd: float) -> dict[str, Any]:
        load_env_file(".env.finance")
        exchange = os.environ.get("CEX_EXECUTION_EXCHANGE", "bybit").lower()
        if exchange == "bybit" and not os.environ.get("BYBIT_API_KEY"):
            return {"status": "skipped", "venue": self.name, "reason": "no BYBIT_API_KEY"}
        if exchange == "okx" and not os.environ.get("OKX_API_KEY"):
            return {"status": "skipped", "venue": self.name, "reason": "no OKX_API_KEY"}
        return {
            "status": "stub",
            "venue": self.name,
            "exchange": exchange,
            "market_id": market_id,
            "side": side,
            "size_usd": size_usd,
            "note": "Wire signed REST order for chosen CEX",
        }

    def check_health(self) -> dict[str, Any]:
        sample = self._fetch_bybit_ticker(self.symbols[0]) if self.symbols else None
        return {
            "venue": self.name,
            "ok": sample is not None,
            "detail": "bybit ticker ok" if sample else "bybit ticker unreachable",
        }
