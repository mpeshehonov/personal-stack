"""Tests for apply-path classification (direct contact vs aggregator bots)."""

from __future__ import annotations

import unittest

from job_hunt.apply_path import analyze_apply_path, extract_company_name
from opportunity.actions import decide_next_action, action_how_ru
from opportunity.models import NextAction


class ApplyPathTest(unittest.TestCase):
    def test_runello_is_research_not_bot_apply(self) -> None:
        text = (
            "Frontend developer\n"
            "Стек: React, TypeScript\n"
            "Компания «ЮниВеб» была основана в 2009 году.\n"
            "Откликнуться через Runello-бот ↓"
        )
        hrefs = [
            "https://t.me/RunelloBot/runello?startapp=eyJvcmRlciI6MTU1fQ",
        ]
        path = analyze_apply_path(
            text=text,
            hrefs=hrefs,
            channel="runello_rus_frontend",
            post_url="https://t.me/runello_rus_frontend/4136",
        )
        self.assertTrue(path["aggregator"])
        self.assertFalse(path["actionable"])
        self.assertEqual(path["strategy"], "research_company")
        self.assertEqual(path["company"], "ЮниВеб")
        self.assertIn("Не через Runello", path["apply_hint_ru"])

    def test_direct_ashby_url(self) -> None:
        path = analyze_apply_path(
            text="Staff Frontend at Phantom\nContact via link",
            hrefs=[
                "https://jobs.ashbyhq.com/phantom/1a7b0f14-556b-4bb0-b1c1-43702d6b56c3"
            ],
            channel="job_react",
            post_url="https://t.me/job_react/1",
        )
        self.assertTrue(path["actionable"])
        self.assertEqual(path["strategy"], "direct_url")
        self.assertFalse(path["aggregator"])

    def test_direct_telegram_contact(self) -> None:
        path = analyze_apply_path(
            text="Пишите @hr_ivanov или на jobs@acme.dev\nКомпания: Acme",
            hrefs=[],
            channel="frontend_rabota",
        )
        self.assertEqual(path["strategy"], "direct_tg")
        self.assertIn("@hr_ivanov", path["telegrams"])
        self.assertIn("jobs@acme.dev", path["emails"])

    def test_company_patterns(self) -> None:
        self.assertEqual(extract_company_name("Компания: AGIMA\nЗП: 250"), "AGIMA")
        self.assertEqual(
            extract_company_name("Company : Phantom\nSalary"), "Phantom"
        )

    def test_decide_action_research_for_aggregator(self) -> None:
        action, prio = decide_next_action(
            status="new",
            scores={"overall_score": 82, "probability": {"score": 40}},
            analysis={
                "actionable": False,
                "paywall": True,
                "apply_strategy": "research_company",
                "aggregator": True,
            },
        )
        self.assertEqual(action, NextAction.RESEARCH_COMPANY.value)
        self.assertEqual(prio, "HIGH")

    def test_decide_action_write_contact(self) -> None:
        action, _ = decide_next_action(
            status="new",
            scores={"overall_score": 80, "probability": {"score": 70}},
            analysis={
                "actionable": True,
                "paywall": False,
                "apply_strategy": "direct_tg",
                "apply_contacts": {"telegrams": ["@hr_ivanov"]},
            },
        )
        self.assertEqual(action, NextAction.WRITE_TO_CONTACT.value)

    def test_runello_sibling_not_contact(self) -> None:
        path = analyze_apply_path(
            text="Senior Frontend\nОткликнуться через Runello-бот",
            hrefs=[
                "https://t.me/runello_rus_html/1467",
                "https://t.me/RunelloBot/runello?startapp=xxx",
            ],
            channel="runello_rus_frontend",
        )
        self.assertFalse(path["actionable"])
        self.assertEqual(path["telegrams"], [])
        self.assertEqual(path["strategy"], "research_company")


if __name__ == "__main__":
    unittest.main()
