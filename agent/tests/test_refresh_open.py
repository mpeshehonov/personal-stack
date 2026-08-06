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

    def test_figma_not_marketplace(self) -> None:
        out = validate_open_url("https://www.figma.com/design/abc/Foo")
        self.assertFalse(out["ok"])
        self.assertEqual(out.get("reason"), "not_marketplace")

    def test_titles_compatible(self) -> None:
        from opportunity.refresh_open import titles_compatible

        self.assertTrue(
            titles_compatible(
                "Заказ: Верстка лендинга по макету",
                "Верстка лендинга по макету (PSD)",
            )
        )
        self.assertFalse(
            titles_compatible(
                "Заказ: Веб-приложение, аналог интранета",
                "Доработать лендинг",
            )
        )

    def test_tg_post_blob_ignores_sibling_links(self) -> None:
        from opportunity.client_scan import extract_marketplace_urls
        from opportunity.refresh_open import _extract_tg_post_blob

        html = """
        <div class="tgme_widget_message_wrap" data-post="projects_fl/1">
          <div class="tgme_widget_message_text">Заказ A <a href="https://kwork.ru/projects/111">x</a></div>
        </div>
        <div class="tgme_widget_message_wrap" data-post="projects_fl/304372">
          <div class="tgme_widget_message_text">Интранет бюджет 30к <a href="https://t.me/projects_fl">ch</a></div>
        </div>
        <div class="tgme_widget_message_wrap" data-post="projects_fl/9">
          <div class="tgme_widget_message_text">Заказ B <a href="https://kwork.ru/projects/999">y</a></div>
        </div>
        """
        blob = _extract_tg_post_blob(html, channel="projects_fl", post_id="304372")
        self.assertIn("Интранет", blob)
        self.assertEqual(extract_marketplace_urls(blob), [])

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
