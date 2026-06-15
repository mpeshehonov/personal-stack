"""Finance executor orchestrating risk + venues + wallet."""

from __future__ import annotations

import logging
from typing import Any

from finance.grid_calculator import grid_preview_for_markets
from finance.goal_tracker import goal_progress, milestone_progress
from finance.polymarket_client import PolymarketClient, is_geoblocked
from finance.risk_engine import RiskEngine, TradeProposal
from finance.signal_rules import filter_scan_markets
from finance.venue_base import TradeVenue, get_enabled_venues
from finance.wallet_manager import WalletManager
from orchestrator.state import log_finance

logger = logging.getLogger(__name__)


class FinanceExecutor:
    def __init__(self) -> None:
        self.risk = RiskEngine()
        self.venues: list[TradeVenue] = get_enabled_venues()
        self._venue_by_name = {v.name: v for v in self.venues}
        self.poly = PolymarketClient()
        self.wallet = WalletManager()

    def _market_title(self, market: dict[str, Any] | None = None, **fields: Any) -> str:
        if market:
            for key in ("question", "title", "market_title", "description"):
                val = market.get(key)
                if val:
                    return str(val)
        for key in ("market_title", "question", "title"):
            val = fields.get(key)
            if val:
                return str(val)
        return ""

    def _log_paper_trade(
        self, proposal: TradeProposal, market_title: str = ""
    ) -> None:
        payload: dict[str, Any] = dict(proposal.__dict__)
        if market_title:
            payload["market_title"] = market_title
        log_finance("paper_trade", payload)

    def _try_live_order(
        self,
        proposal: TradeProposal,
        market_title: str = "",
        venue_name: str = "polymarket",
    ) -> dict[str, Any]:
        if venue_name == "polymarket":
            geoblock = self.poly.check_geoblock()
            if is_geoblocked(geoblock):
                result = {
                    "status": "blocked",
                    "reason": "geoblocked",
                    "venue": venue_name,
                    "geoblock": geoblock,
                    "market_id": proposal.market_id,
                    "side": proposal.side,
                    "size_usd": proposal.size_usd,
                }
                log_finance(
                    "order_blocked",
                    {
                        "venue": venue_name,
                        "market_id": proposal.market_id,
                        "market_title": market_title,
                        "side": proposal.side,
                        "size_usd": proposal.size_usd,
                        "geoblock": geoblock,
                    },
                )
                return result
        venue = self._venue_by_name.get(venue_name)
        if not venue:
            return {"status": "skipped", "reason": f"unknown venue: {venue_name}"}
        return venue.place_order(
            proposal.market_id, proposal.side, proposal.size_usd
        )

    def daily_analysis(self) -> dict[str, Any]:
        all_markets: list[dict[str, Any]] = []
        scan_by_venue: dict[str, int] = {}
        venue_health: list[dict[str, Any]] = []
        for venue in self.venues:
            venue_health.append(venue.check_health())
            batch = venue.get_markets(limit=10)
            scan_by_venue[venue.name] = len(batch)
            all_markets.extend(batch)

        tradeable, rejected = filter_scan_markets(all_markets)

        grid_previews = grid_preview_for_markets(tradeable)

        proposals: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []

        for m in tradeable[:3]:
            market_id = str(m.get("condition_id") or m.get("id") or "")
            venue_name = str(
                m.get("venue") or (self.venues[0].name if self.venues else "polymarket")
            )
            if not market_id:
                continue
            market_title = self._market_title(market=m)
            proposal = TradeProposal(
                market_id=market_id,
                side="buy",
                size_usd=min(25.0, self.risk.max_trade),
                reason=f"Daily scan ({venue_name}) — low-size exploratory",
            )
            decision = self.risk.evaluate(proposal)
            proposals.append(
                {
                    "proposal": {**proposal.__dict__, "venue": venue_name},
                    "market_title": market_title,
                    "venue": venue_name,
                    "decision": decision.reason,
                }
            )
            if decision.approved and decision.proposal:
                if self.risk.live:
                    exec_result = self._try_live_order(
                        decision.proposal,
                        market_title=market_title,
                        venue_name=venue_name,
                    )
                    results.append(exec_result)
                else:
                    self._log_paper_trade(decision.proposal, market_title)

        summary = {
            "venues": [v.name for v in self.venues],
            "venue_health": venue_health,
            "scan_by_venue": scan_by_venue,
            "markets_scanned": len(all_markets),
            "markets_after_filters": len(tradeable),
            "markets_rejected": len(rejected),
            "rejection_samples": rejected[:5],
            "grid_previews": grid_previews,
            "proposals": proposals,
            "executions": results,
            "goal": goal_progress(),
            "milestone": milestone_progress(),
            "today_pnl_note": "see finance_log in state.sqlite",
        }
        log_finance("daily_analysis", summary)
        return summary

    def process_agent_proposals(
        self, proposals: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        outcomes = []
        for p in proposals:
            market_title = self._market_title(**p)
            decision = self.risk.evaluate_dict(p)
            entry: dict[str, Any] = {
                "approved": decision.approved,
                "reason": decision.reason,
                "market_id": p.get("market_id"),
                "market_title": market_title,
            }
            if decision.approved and decision.proposal:
                venue_name = str(p.get("venue") or "polymarket")
                if self.risk.live:
                    entry["execution"] = self._try_live_order(
                        decision.proposal,
                        market_title=market_title,
                        venue_name=venue_name,
                    )
                else:
                    self._log_paper_trade(decision.proposal, market_title)
                    entry["paper"] = True
            outcomes.append(entry)
        if outcomes:
            log_finance(
                "agent_proposals",
                {"count": len(outcomes), "outcomes": outcomes},
            )
        return outcomes
