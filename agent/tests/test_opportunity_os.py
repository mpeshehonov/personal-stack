"""Tests for Opportunity OS core (Jobs vertical)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def _setup_temp_stack(tmp: Path) -> None:
    (tmp / "agent" / "memory").mkdir(parents=True)
    (tmp / "site" / "content" / "resume").mkdir(parents=True)
    (tmp / "secrets").mkdir(parents=True)
    resume = {
        "skills": ["React", "TypeScript", "Next.js", "JavaScript"],
        "title": "Senior Frontend Engineer",
    }
    (tmp / "site" / "content" / "resume" / "resume.json").write_text(
        json.dumps(resume), encoding="utf-8"
    )


class OpportunityOSTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        _setup_temp_stack(self.tmp)
        self.stack = str(self.tmp)
        os.environ["STACK_DIR"] = self.stack

        # Reload config-bound modules with new STACK_DIR
        import importlib
        import orchestrator.config as cfg

        importlib.reload(cfg)
        import orchestrator.state as state

        importlib.reload(state)
        import opportunity.profile as profile
        import opportunity.repository as repo
        import opportunity.migrate as migrate
        import opportunity.scoring as scoring
        import opportunity.feedback as feedback
        import opportunity.actions as actions
        import opportunity.brief as brief
        import opportunity.services as services
        import opportunity.preferences as preferences
        import job_hunt.dedup as dedup
        import job_hunt.matcher as matcher

        for mod in (
            profile,
            repo,
            migrate,
            scoring,
            feedback,
            actions,
            brief,
            services,
            preferences,
            dedup,
            matcher,
            state,
        ):
            importlib.reload(mod)

        self.state = state
        self.profile = profile
        self.repo = repo
        self.migrate = migrate
        self.scoring = scoring
        self.feedback = feedback
        self.actions = actions
        self.brief = brief
        self.services = services
        self.preferences = preferences
        self.dedup = dedup
        self.matcher = matcher

        state.init_db()
        profile.ensure_profile()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _sample_vacancy(self, **over) -> dict:
        v = {
            "id": "1001",
            "name": "Senior Frontend Engineer",
            "alternate_url": "https://hh.ru/vacancy/1001",
            "employer": {"name": "Acme"},
            "key_skills": [{"name": "React"}, {"name": "TypeScript"}],
            "schedule": {"id": "remote", "name": "удалённо"},
            "salary": {"from": 3500, "currency": "USD"},
            "snippet": {
                "requirement": "React TypeScript Next.js",
                "responsibility": "product UI remote",
            },
            "area": {"name": "Remote"},
            "_source": "hh",
            "_actionable": True,
            "_paywall": False,
            "_published_at": "2026-07-29T10:00:00+00:00",
        }
        v.update(over)
        return v

    def test_dedupe_fingerprint(self) -> None:
        a = self._sample_vacancy()
        b = self._sample_vacancy(id="1002", alternate_url="https://other/1002")
        out, skipped = self.dedup.dedupe_vacancies([a, b])
        self.assertEqual(len(out), 1)
        self.assertEqual(skipped, 1)

    def test_stage_a_and_overall_deterministic(self) -> None:
        from opportunity.models import ScoreComponent

        v = self._sample_vacancy()
        ok, match, reasons = self.scoring.stage_a_filter(v, min_match=70)
        self.assertTrue(ok)
        self.assertGreaterEqual(match, 70)
        b1 = self.scoring.score_opportunity(v, match_score=match, match_reasons=reasons)
        b2 = self.scoring.score_opportunity(v, match_score=match, match_reasons=reasons)
        self.assertEqual(b1.overall, b2.overall)
        self.assertIn("fit", b1.to_dict())
        self.assertEqual(
            self.scoring.compute_overall(
                {
                    "fit": ScoreComponent(100, []),
                    "income": ScoreComponent(100, []),
                    "growth": ScoreComponent(100, []),
                    "probability": ScoreComponent(100, []),
                    "strategic": ScoreComponent(100, []),
                    "urgency": ScoreComponent(100, []),
                },
                {
                    "fit": 1,
                    "income": 0,
                    "growth": 0,
                    "probability": 0,
                    "strategic": 0,
                    "urgency": 0,
                },
            ),
            100,
        )

    def test_hirify_paywall_lowers_probability(self) -> None:
        v = self._sample_vacancy(
            _source="hirify",
            _paywall=True,
            _actionable=False,
            employer={"name": ""},
            alternate_url="https://hirify.me/jobs/x",
        )
        bundle = self.scoring.score_opportunity(v, match_score=90, match_reasons=["senior"])
        self.assertLess(bundle.probability.score, 55)
        action, _ = self.actions.decide_next_action(
            status="new",
            scores=bundle.to_dict(),
            analysis={"paywall": True, "actionable": False},
        )
        self.assertEqual(action, "RESEARCH_COMPANY")

    def test_migration_from_job_leads(self) -> None:
        lead_id = self.state.add_job_lead(
            source="hh",
            external_id="42",
            url="https://hh.ru/vacancy/42",
            title="Senior React Developer",
            company="TestCo",
            match_score=80,
            match_reasons_json='["senior (+20)"]',
            status="new",
        )
        result = self.migrate.migrate_opportunity_core(rescore=True, repair_hirify=True)
        self.assertGreaterEqual(result["created"] + result["updated"], 1)
        opp = self.repo.get_opportunity_by_lead(lead_id)
        self.assertIsNotNone(opp)
        self.assertEqual(opp.type.value, "JOB")
        self.assertGreater(opp.overall_score, 0)

    def test_feedback_paywall_preserves_hirify_weight(self) -> None:
        from job_hunt.sources import apply_feedback

        self.state.set_job_source(
            "hirify", kind="board", weight=1.2, enabled=True, status="active"
        )
        v = self._sample_vacancy(
            id="h1",
            _source="hirify",
            alternate_url="https://hirify.me/jobs/h1",
            _paywall=True,
            _actionable=False,
        )
        lead_id = self.state.add_job_lead(
            source="hirify",
            external_id="h1",
            url=v["alternate_url"],
            title=v["name"],
            company="",
            match_score=88,
            match_reasons_json='["senior"]',
        )
        self.services.upsert_from_job_lead(
            lead_id=lead_id,
            vacancy=v,
            match_score=88,
            match_reasons=["senior"],
        )
        result = apply_feedback(lead_id, "dislike", note="")
        self.assertTrue(result.get("source_weight_skipped"))
        self.assertEqual(result["weight_before"], result["weight_after"])
        row = self.state.get_job_source("hirify")
        self.assertTrue(row["enabled"])
        self.assertGreaterEqual(float(row["weight"]), 1.0)

    def test_feedback_bad_fit_punishes_source(self) -> None:
        from job_hunt.sources import apply_feedback

        self.state.set_job_source(
            "hirehi", kind="board", weight=1.0, enabled=True, status="active"
        )
        lead_id = self.state.add_job_lead(
            source="hirehi",
            external_id="x1",
            url="https://hirehi.ru/x1",
            title="Junior HTML",
            company="Spam",
            match_score=70,
        )
        self.services.upsert_from_job_lead(
            lead_id=lead_id,
            vacancy=self._sample_vacancy(id="x1", _source="hirehi", name="Junior HTML"),
            match_score=70,
            match_reasons=[],
        )
        result = apply_feedback(lead_id, "dislike", note="bad_fit")
        self.assertFalse(result.get("source_weight_skipped"))
        self.assertLess(result["weight_after"], result["weight_before"])

    def test_next_action_transitions(self) -> None:
        scores = {"overall_score": 90, "probability": {"score": 70}}
        self.assertEqual(
            self.actions.decide_next_action(status="interview", scores=scores)[0],
            "PREPARE_INTERVIEW",
        )
        self.assertEqual(
            self.actions.decide_next_action(status="offer", scores=scores)[0],
            "EVALUATE_OFFER",
        )
        self.assertEqual(
            self.actions.decide_next_action(status="applied", scores=scores)[0],
            "FOLLOW_UP",
        )

    def test_brief_renders(self) -> None:
        v = self._sample_vacancy()
        lead_id = self.state.add_job_lead(
            source="hh",
            external_id="b1",
            url=v["alternate_url"],
            title=v["name"],
            company="Acme",
            match_score=90,
            match_reasons_json='["senior"]',
        )
        self.services.upsert_from_job_lead(
            lead_id=lead_id, vacancy=v, match_score=90, match_reasons=["senior"]
        )
        data = self.brief.build_opportunity_brief(top_n=5, actions_n=3)
        self.assertIn("Бриф возможностей", data["header"])
        self.assertIn("Воронка", data["header"])
        self.assertIn("Новые:", data["header"])
        self.assertTrue(data["cards"])
        text = self.brief.format_opportunity_brief(top_n=5, actions_n=3)
        self.assertIn("Бриф возможностей", text)

    def test_legacy_scan_compat_add_lead(self) -> None:
        """Old job_hunt storage path still works."""
        lid = self.state.add_job_lead(
            source="habr",
            external_id="z",
            url="https://career.habr.com/z",
            title="Senior Frontend",
            company="HabrCo",
            match_score=75,
        )
        self.assertIsNotNone(self.state.get_job_lead(lid))
        leads = self.state.list_job_leads(status="new", limit=5, min_score=70)
        self.assertTrue(any(r["id"] == lid for r in leads))


if __name__ == "__main__":
    unittest.main()
