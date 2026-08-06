"""Tests for open-link revalidation helpers."""

from __future__ import annotations

import unittest
from unittest import mock

from opportunity.refresh_open import validate_hh_vacancy_url, validate_open_url
from telegram_bot.jobs_ui import parse_opp_callback, parse_menu_text


class RefreshOpenTest(unittest.TestCase):
    def test_dead_habr_fails(self) -> None:
        self.assertFalse(validate_open_url("https://u.habr.com/dead")["ok"])

    def test_hh_archived(self) -> None:
        with mock.patch(
            "job_hunt.hh_client.fetch_hh_vacancy_api",
            return_value={"archived": True, "name": "X"},
        ):
            out = validate_hh_vacancy_url("https://hh.ru/vacancy/12345")
        self.assertFalse(out["ok"])

    def test_hh_open(self) -> None:
        with mock.patch(
            "job_hunt.hh_client.fetch_hh_vacancy_api",
            return_value={"archived": False, "name": "FE"},
        ):
            out = validate_hh_vacancy_url("https://hh.ru/vacancy/12345")
        self.assertTrue(out["ok"])
        self.assertEqual(out.get("title"), "FE")

    def test_hh_blocked_stays_open(self) -> None:
        with mock.patch("job_hunt.hh_client.fetch_hh_vacancy_api", return_value=None):
            out = validate_hh_vacancy_url("https://hh.ru/vacancy/12345")
        self.assertTrue(out["ok"])
        self.assertEqual(out.get("reason"), "hh_fetch_blocked")

    def test_opp_nav_callbacks(self) -> None:
        self.assertEqual(parse_opp_callback("o:more"), ("more", None))
        self.assertEqual(parse_opp_callback("o:scan"), ("scan", None))
        self.assertEqual(parse_opp_callback("o:refresh"), ("refresh", None))
        self.assertEqual(parse_opp_callback("o:like:42"), ("like", 42))

    def test_menu_clients_refresh(self) -> None:
        self.assertEqual(parse_menu_text("Заказы"), "clients")
        self.assertEqual(parse_menu_text("Обновить"), "refresh")
        self.assertEqual(parse_menu_text("Скан заказов"), "client_scan")


if __name__ == "__main__":
    unittest.main()
