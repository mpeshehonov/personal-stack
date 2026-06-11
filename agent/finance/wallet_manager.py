"""Wallet manager: profit split 50/50 on realized gains."""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from orchestrator.config import load_env_file
from orchestrator.state import log_finance

logger = logging.getLogger(__name__)

POLYGON_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def is_valid_polygon_address(address: str) -> bool:
    return bool(POLYGON_ADDRESS_RE.match(address.strip()))


class WalletManager:
    def __init__(self) -> None:
        load_env_file(".env.finance")
        self.your_wallet = os.environ.get("YOUR_WALLET_ADDRESS", "").strip()
        self.live = os.environ.get("FINANCE_LIVE", "false").lower() == "true"
        if self.your_wallet and not is_valid_polygon_address(self.your_wallet):
            logger.warning(
                "YOUR_WALLET_ADDRESS is not a valid Polygon address: %s",
                self.your_wallet,
            )

    def validate_withdrawal_address(self) -> tuple[bool, str]:
        if not self.your_wallet:
            return False, "YOUR_WALLET_ADDRESS not configured"
        if not is_valid_polygon_address(self.your_wallet):
            return False, "YOUR_WALLET_ADDRESS must be a 0x-prefixed 40-hex Polygon address"
        return True, "ok"

    def split_profit(self, profit_usd: float) -> dict[str, Any]:
        if profit_usd <= 0:
            return {"action": "none", "profit_usd": profit_usd}
        half = profit_usd / 2
        result: dict[str, Any] = {
            "action": "split",
            "profit_usd": profit_usd,
            "withdraw_usd": half,
            "reinvest_usd": half,
            "destination": self.your_wallet,
            "live": self.live,
        }
        valid, reason = self.validate_withdrawal_address()
        if not valid:
            result["tx_status"] = f"skipped — {reason}"
            log_finance("profit_split", result, pnl_usd=profit_usd)
            return result
        if self.live:
            # Production: on-chain USDC transfer via web3
            result["tx_status"] = "stub — implement web3 transfer"
            logger.info("Would withdraw $%.2f to %s", half, self.your_wallet)
        else:
            result["tx_status"] = "paper — logged only"
        log_finance("profit_split", result, pnl_usd=profit_usd)
        return result
