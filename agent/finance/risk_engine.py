"""Hard-coded risk limits — not LLM enforced."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from orchestrator.config import load_env_file
from orchestrator.state import today_pnl


@dataclass
class TradeProposal:
    market_id: str
    side: str
    size_usd: float
    reason: str


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    proposal: TradeProposal | None = None


class RiskEngine:
    def __init__(self) -> None:
        load_env_file(".env.finance")
        self.max_trade = float(os.environ.get("MAX_TRADE_USD", "75"))
        self.daily_stop = float(os.environ.get("DAILY_STOP_LOSS_USD", "100"))
        self.max_open = int(os.environ.get("MAX_OPEN_POSITIONS", "3"))
        self.live = os.environ.get("FINANCE_LIVE", "false").lower() == "true"
        self.allowed_markets = {
            m.strip()
            for m in os.environ.get("ALLOWED_MARKETS", "").split(",")
            if m.strip()
        }

    def evaluate(self, proposal: TradeProposal, open_positions: int = 0) -> RiskDecision:
        if proposal.size_usd <= 0:
            return RiskDecision(False, "size must be positive", proposal)
        if proposal.size_usd > self.max_trade:
            return RiskDecision(
                False,
                f"size ${proposal.size_usd} exceeds max ${self.max_trade}",
                proposal,
            )
        if open_positions >= self.max_open:
            return RiskDecision(False, "max open positions reached", proposal)
        pnl = today_pnl()
        if pnl <= -self.daily_stop:
            return RiskDecision(
                False,
                f"daily stop-loss hit (PnL ${pnl})",
                proposal,
            )
        if self.allowed_markets and proposal.market_id not in self.allowed_markets:
            return RiskDecision(False, "market not in whitelist", proposal)
        if not self.live:
            return RiskDecision(
                True,
                "approved (paper mode — not executed on-chain)",
                proposal,
            )
        return RiskDecision(True, "approved for live execution", proposal)

    def evaluate_dict(self, data: dict[str, Any]) -> RiskDecision:
        proposal = TradeProposal(
            market_id=str(data.get("market_id", "")),
            side=str(data.get("side", "buy")),
            size_usd=float(data.get("size_usd", 0)),
            reason=str(data.get("reason", "")),
        )
        return self.evaluate(proposal, int(data.get("open_positions", 0)))
