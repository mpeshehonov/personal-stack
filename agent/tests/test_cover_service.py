"""Cover letter pipeline: parse inputs, prepositions, HH length."""

from __future__ import annotations

import unittest

from job_hunt.cover_service import looks_like_cover_request, parse_cover_request
from job_hunt.drafter import draft_cover_hh, humanize_cover_text


class CoverServiceTest(unittest.TestCase):
    def test_looks_like_cover_with_url(self) -> None:
        self.assertTrue(
            looks_like_cover_request(
                "нужен сопровод https://hh.ru/vacancy/134802022 для хх"
            )
        )

    def test_looks_like_cover_with_paste(self) -> None:
        blob = "сопровод для тг\n" + ("Frontend React TypeScript требования " * 20)
        self.assertTrue(looks_like_cover_request(blob))

    def test_parse_hh_url_channel(self) -> None:
        req = parse_cover_request(
            "/cover и на эту нужен сопровод для отклика на хх ру "
            "https://hh.ru/vacancy/134802022?from=share_ios"
        )
        self.assertEqual(req.channel, "hh")
        self.assertTrue(any("hh.ru/vacancy/134802022" in u for u in req.urls))

    def test_parse_tg_hirify(self) -> None:
        req = parse_cover_request(
            "/ask https://hirify.me/jobs/792652-frontend-developer-reacttypescript "
            "нужен сопровод для отклика в тг без своих комментариев"
        )
        self.assertEqual(req.channel, "tg")
        self.assertTrue(req.raw_only)
        self.assertTrue(any("hirify.me" in u for u in req.urls))

    def test_parse_lead_id(self) -> None:
        req = parse_cover_request("сопровод 42 tg")
        self.assertEqual(req.lead_id, 42)
        self.assertEqual(req.channel, "tg")

    def test_preposition_fix(self) -> None:
        fixed = humanize_cover_text(
            "На X5 Tech делал формы. На Citilink каталог. На НЛМК SPA."
        )
        self.assertIn("В X5 Tech", fixed)
        self.assertIn("В Citilink", fixed)
        self.assertIn("В НЛМК", fixed)
        self.assertNotIn("На X5", fixed)
        self.assertNotIn("На Citilink", fixed)

    def test_hh_draft_not_tiny(self) -> None:
        lead = {
            "title": "Senior frontend (платформа ЭДО)",
            "company": "Тензор",
            "description_snippet": "React TypeScript enterprise формы согласования ЭДО",
            "skills_json": '["React", "TypeScript"]',
            "source": "hh",
            "external_id": "",
            "url": "https://hh.ru/vacancy/1",
        }
        body = draft_cover_hh(lead)
        self.assertGreaterEqual(len(body), 600)
        self.assertIn("В X5", body)
        self.assertNotIn("На X5", body)


if __name__ == "__main__":
    unittest.main()
