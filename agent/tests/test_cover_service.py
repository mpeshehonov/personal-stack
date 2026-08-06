"""Cover letter pipeline: parse inputs, prepositions, HH length."""

from __future__ import annotations

import unittest

from job_hunt.cover_service import (
    _extract_jd_meta,
    looks_like_cover_request,
    parse_cover_request,
)
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
            "/cover hh https://hh.ru/vacancy/134802022?from=share_ios"
        )
        self.assertEqual(req.channel, "hh")
        self.assertTrue(any("hh.ru/vacancy/134802022" in u for u in req.urls))

    def test_parse_tg_hirify(self) -> None:
        req = parse_cover_request(
            "/cover tg https://hirify.me/jobs/792652-frontend-developer-reacttypescript"
        )
        self.assertEqual(req.channel, "tg")
        self.assertTrue(req.raw_only)
        self.assertTrue(any("hirify.me" in u for u in req.urls))

    def test_explicit_tg_wins_over_hh_url(self) -> None:
        req = parse_cover_request("/cover tg https://hh.ru/vacancy/123456")
        self.assertEqual(req.channel, "tg")
        self.assertTrue(any("hh.ru/vacancy/123456" in u for u in req.urls))

    def test_parse_lead_id(self) -> None:
        req = parse_cover_request("/cover 42 tg")
        self.assertEqual(req.lead_id, 42)
        self.assertEqual(req.channel, "tg")

    def test_parse_tg_multiline_paste(self) -> None:
        raw = (
            "/cover tg\n"
            "Senior Frontend Developer (React)\n"
            "Компания: Tango\n"
            "Локация: Limassol, Cyprus\n"
            "Ищем Senior Frontend Developer в продуктовую команду Tango.\n"
            "Стек: React, TypeScript, Redux Toolkit.\n"
        )
        req = parse_cover_request(raw)
        self.assertEqual(req.channel, "tg")
        self.assertIn("\n", req.vacancy_text)
        self.assertIn("Компания: Tango", req.vacancy_text)
        title, company = _extract_jd_meta(req.vacancy_text)
        self.assertEqual(company, "Tango")
        self.assertIn("Senior Frontend", title)
        self.assertLess(len(company), 40)

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


    def test_parse_jobposting_blocks(self) -> None:
        from job_hunt.hh_client import _parse_jobposting_blocks

        html = """
        <script type="application/ld+json">
        {"@context":"https://schema.org/","@type":"JobPosting",
         "title":"Фронтенд-разработчик",
         "description":"<p>React Native</p>",
         "hiringOrganization":{"@type":"Organization","name":"Acme"}}
        </script>
        """
        job = _parse_jobposting_blocks(html)
        self.assertIsNotNone(job)
        assert job is not None
        self.assertEqual(job["title"], "Фронтенд-разработчик")
        self.assertEqual(job["hiringOrganization"]["name"], "Acme")

    def test_hh_blocked_error_mentions_paste(self) -> None:
        from unittest import mock

        from job_hunt.cover_service import resolve_vacancy, parse_cover_request

        req = parse_cover_request(
            "/cover hh https://hh.ru/vacancy/135875219?from=share_ios"
        )
        with mock.patch("job_hunt.cover_service.fetch_hh_vacancy", return_value=None):
            with mock.patch("job_hunt.cover_service.fetch_generic_url", return_value=None):
                with self.assertRaises(ValueError) as ctx:
                    resolve_vacancy(req)
        self.assertIn("вставь текст", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
