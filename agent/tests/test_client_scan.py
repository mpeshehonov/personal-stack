"""CLIENT freelance scan — live sources only, reject dead Habr links."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from opportunity.client_scan import (
    is_dead_url,
    is_fresh,
    pick_apply_url,
    score_order,
)


class ClientScanTest(unittest.TestCase):
    def test_rejects_dead_habr_urls(self) -> None:
        self.assertTrue(is_dead_url("https://u.habr.com/28LcH"))
        self.assertTrue(is_dead_url("https://freelance.habr.com/tasks/123"))
        self.assertFalse(is_dead_url("https://www.fl.ru/projects/5516235/x.html"))
        self.assertFalse(is_dead_url("https://kwork.ru/projects/3227860"))

    def test_freshness_gate(self) -> None:
        now = datetime.now(timezone.utc)
        self.assertTrue(is_fresh(now - timedelta(hours=12)))
        self.assertFalse(is_fresh(now - timedelta(hours=100)))
        self.assertFalse(is_fresh(None))

    def test_pick_apply_prefers_marketplace_over_tg(self) -> None:
        url = pick_apply_url(
            [
                "https://t.me/projects_fl",
                "https://u.habr.com/dead",
                "https://kwork.ru/projects/3227860",
            ],
            tg_fallback="https://t.me/projects_fl/1",
        )
        self.assertEqual(url, "https://kwork.ru/projects/3227860")

    def test_score_keeps_react(self) -> None:
        s = score_order("Доработка фронта на React", "админка", "15 000 руб")
        self.assertTrue(s["keep"])

    def test_score_drops_video(self) -> None:
        s = score_order("Ролик на 43-45 сек", "монтаж", "3500 руб")
        self.assertFalse(s["keep"])


if __name__ == "__main__":
    unittest.main()
