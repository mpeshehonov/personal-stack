"""CLIENT freelance scan — parse Habr digests + score FE orders."""

from __future__ import annotations

import unittest

from opportunity.client_scan import parse_habr_digest_items, score_client_order


DIGEST = """
Подборка заказов в категории Разработка (Фронтенд):
1. Перенести текущую версию приожения c react на next (цена договорная) https://u.habr.com/28LcH
2. Верстка макета figma под wp  (1 000 руб. за проект) https://u.habr.com/Stj4F
3. Внести доработки по frontend-части на сайт на NextJS (цена договорная) https://u.habr.com/KhFTH
4. Разработать интерфейс личного кабинета сервиса аналитики на реакте (40 000 руб. за проект) https://u.habr.com/H0Pj6
5. Разработать телеграмм бота Quiz (цена договорная) https://u.habr.com/oLxp9
"""


class ClientScanTest(unittest.TestCase):
    def test_parse_digest_items(self) -> None:
        items = parse_habr_digest_items(DIGEST)
        self.assertGreaterEqual(len(items), 4)
        self.assertEqual(items[0]["category"], "frontend")
        self.assertTrue(items[0]["url"].startswith("https://u.habr.com/"))

    def test_score_keeps_react_next(self) -> None:
        s = score_client_order(
            "Перенести приложение c react на next",
            "цена договорная",
            category="frontend",
        )
        self.assertTrue(s["keep"])
        self.assertGreaterEqual(s["score"], 70)

    def test_score_drops_cheap_bitrixy(self) -> None:
        s = score_client_order(
            "Верстка макета figma под wp",
            "1 000 руб. за проект",
            category="frontend",
        )
        self.assertFalse(s["keep"])

    def test_score_drops_python_bot(self) -> None:
        s = score_client_order(
            "Разработать телеграмм бота Quiz",
            "цена договорная",
            category="digest",
        )
        self.assertFalse(s["keep"])
        s2 = score_client_order(
            "Написание чат бота в Телеграм и реферальной системы на Питоне",
            "40 000 руб. за проект",
            category="frontend",
        )
        self.assertFalse(s2["keep"])

    def test_score_keeps_cabinet_react(self) -> None:
        s = score_client_order(
            "Разработать интерфейс личного кабинета на реакте",
            "40 000 руб. за проект",
            category="frontend",
        )
        self.assertTrue(s["keep"])
        self.assertGreaterEqual(s["score"], 80)


if __name__ == "__main__":
    unittest.main()
