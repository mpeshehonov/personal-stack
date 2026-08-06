"""Smoke tests for FL.ru vacancy shaping."""

from __future__ import annotations

import unittest

from job_hunt.fl_vacancies import fl_to_vacancy_shape
from job_hunt.sources import source_key_for_vacancy


class FlVacanciesTest(unittest.TestCase):
    def test_shape_and_source_key(self) -> None:
        v = fl_to_vacancy_shape(
            external_id="12345",
            title="Frontend React",
            url="https://www.fl.ru/projects/12345/frontend-react.html",
            snippet="React Next.js",
        )
        self.assertEqual(v["_source"], "fl")
        self.assertEqual(v["id"], "12345")
        self.assertEqual(source_key_for_vacancy(v), "fl")
        self.assertIn("fl.ru", v["alternate_url"])


if __name__ == "__main__":
    unittest.main()
