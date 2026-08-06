"""Tests for company research / open-url picking."""

from __future__ import annotations

import unittest

from job_hunt.company_research import (
    build_research_links,
    is_google_search_url,
    is_useless_open_url,
    pick_open_url,
)


class CompanyResearchTest(unittest.TestCase):
    def test_runello_post_is_useless(self) -> None:
        self.assertTrue(
            is_useless_open_url("https://t.me/runello_rus_frontend/4139")
        )
        self.assertTrue(
            is_useless_open_url(
                "https://t.me/RunelloBot/runello?startapp=eyJvcmRlciI6MTU1fQ"
            )
        )
        self.assertFalse(is_useless_open_url("https://hh.ru/vacancy/123"))
        self.assertTrue(
            is_useless_open_url(
                "https://www.google.com/search?q=Acme+карьера"
            )
        )
        self.assertTrue(is_google_search_url("https://www.google.com/search?q=x"))

    def test_pick_open_prefers_hh_over_runello(self) -> None:
        url = pick_open_url(
            source_url="https://t.me/runello_rus_frontend/100",
            analysis={
                "aggregator": True,
                "company": "Phantom",
                "research": {
                    "hh_vacancy_url": "https://hh.ru/vacancy/999",
                    "hh_search_url": "https://hh.ru/search/vacancy?text=Phantom",
                },
            },
        )
        self.assertEqual(url, "https://hh.ru/vacancy/999")

    def test_pick_open_falls_back_to_hh_search(self) -> None:
        url = pick_open_url(
            source_url="https://t.me/runello_rus_frontend/100",
            analysis={"aggregator": True, "company": "Acme Corp", "research": {}},
        )
        self.assertIn("hh.ru/search", url)
        self.assertIn("Acme", url)

    def test_pick_open_empty_without_company_or_real_link(self) -> None:
        url = pick_open_url(
            source_url="https://t.me/runello_rus_frontend/100",
            analysis={
                "aggregator": True,
                "company": "",
                "research": {
                    "career_search_url": "https://www.google.com/search?q=foo",
                },
            },
        )
        self.assertEqual(url, "")

    def test_pick_open_keeps_fl_and_source_post(self) -> None:
        fl = pick_open_url(
            source_url="https://www.fl.ru/projects/123/foo.html",
            analysis={"research": {}},
        )
        self.assertIn("fl.ru", fl)
        post = pick_open_url(
            source_url="https://t.me/web_zakaz/42",
            analysis={"research": {}},
        )
        self.assertEqual(post, "https://t.me/web_zakaz/42")

    def test_research_links_without_company_uses_title(self) -> None:
        links = build_research_links("", title="Senior Frontend Developer React")
        self.assertIn("career_search_url", links)
        self.assertIn("google.com/search", links["career_search_url"])


if __name__ == "__main__":
    unittest.main()
