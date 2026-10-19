import unittest
from fastapi.testclient import TestClient

from backend.main import app
from backend.recommendation_service import (
    _build_verified_internship_flags,
    _internship_role_match,
    _load_dataset,
    extract_internship_skill_evidence,
)


class InternshipRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)

    def test_internship_tiers_are_relevant_classified_and_disjoint(self):
        cases = [
            ("Data Analyst", ["Python", "SQL", "Excel", "Power BI"], (5, 0, 0)),
            ("Business Analyst", ["Excel", "SQL", "Power BI", "Tableau"], (3, 2, 2)),
            ("Data Scientist", ["Python", "SQL", "Machine Learning", "Pandas"], (1, 0, 2)),
            ("Python Developer", ["Python", "Django", "Flask", "SQL"], (2, 3, 0)),
            ("Software Developer", ["JavaScript", "React", "HTML", "CSS", "Python"], (6, 1, 0)),
            ("Frontend Developer", ["JavaScript", "React", "HTML", "CSS"], (4, 0, 0)),
        ]
        dataset = _load_dataset()
        rows_by_id = {
            str(row["jobid"]): row
            for _, row in dataset.iterrows()
        }

        for role, skills, expected_counts in cases:
            with self.subTest(role=role):
                response = self.client.post(
                    "/recommend",
                    json={
                        "role": role,
                        "skills": skills,
                        "experience": 0,
                        "location": "Any",
                        "work_mode": "Any",
                        "job_type": "Internship",
                    },
                )

                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertTrue(payload["success"])
                result = payload["results"]
                recommendations = result["recommendations"]
                limited = result["limited_skill_overlap_internships"]
                incomplete = result["other_relevant_internships"]
                self.assertEqual(
                    (len(recommendations), len(limited), len(incomplete)),
                    expected_counts,
                )

                section_ids = [
                    [item["job_id"] for item in section]
                    for section in (recommendations, limited, incomplete)
                ]
                for ids in section_ids:
                    self.assertEqual(len(ids), len(set(ids)))
                self.assertTrue(set(section_ids[0]).isdisjoint(section_ids[1]))
                self.assertTrue(set(section_ids[0]).isdisjoint(section_ids[2]))
                self.assertTrue(set(section_ids[1]).isdisjoint(section_ids[2]))

                for item in recommendations + limited + incomplete:
                    self.assertEqual(item["classification"], "Internship")
                    source_row = rows_by_id[item["job_id"]]
                    self.assertTrue(source_row["_is_verified_internship"])
                    skill_sources = extract_internship_skill_evidence(source_row)
                    self.assertTrue(
                        _internship_role_match(source_row, role, skill_sources)[0]
                    )

                self.assertTrue(all(len(item["matched_skills"]) >= 2 for item in recommendations))
                self.assertTrue(all(item["overlap_count"] == 1 for item in limited))
                self.assertTrue(all(item["label"] == "Limited skill overlap" for item in limited))
                self.assertTrue(all(len(item["available_skills"]) < 2 for item in incomplete))
                self.assertTrue(all(item["label"] == "Skill data incomplete" for item in incomplete))
                self.assertLessEqual(
                    result["internship_coverage"]["displayed_listings"],
                    7,
                )
                self.assertEqual(
                    result["internship_coverage"]["displayed_listings"],
                    len(recommendations) + len(limited) + len(incomplete),
                )

    def test_data_analyst_two_skill_internship_matches_remain_scored(self):
        response = self.client.post(
            "/recommend",
            json={
                "role": "Data Analyst",
                "skills": ["Python", "SQL"],
                "experience": 0,
                "location": "Any",
                "work_mode": "Any",
                "job_type": "Internship",
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["results"]
        self.assertEqual(result["summary"]["jobs_analyzed"], 6)
        self.assertEqual(result["summary"]["jobs_recommended"], 3)
        self.assertEqual(len(result["recommendations"]), 3)
        self.assertEqual(len(result["limited_skill_overlap_internships"]), 1)
        self.assertEqual(result["other_relevant_internships"], [])

    def test_internship_skill_extraction_tracks_source_and_respects_negation(self):
        evidence = extract_internship_skill_evidence({
            "title": "Frontend Developer Intern",
            "tagsandskills": "Not Specified",
            "jobdescription": (
                "Build applications with React.js and JS. SQL is not required. "
                "Excel is a plus."
            ),
        })
        self.assertEqual(evidence["react"], {"description"})
        self.assertEqual(evidence["javascript"], {"description"})
        self.assertEqual(evidence["excel"], {"description"})
        self.assertNotIn("sql", evidence)

        mixed_evidence = extract_internship_skill_evidence({
            "title": "Data Analyst Intern",
            "tagsandskills": "Not Specified",
            "jobdescription": "Python is required, but SQL is not required.",
        })
        self.assertEqual(mixed_evidence["python"], {"description"})
        self.assertNotIn("sql", mixed_evidence)

    def test_non_internship_classifier_evidence_is_not_verified(self):
        import pandas as pd

        frame = pd.DataFrame([{
            "title": "Software Development Engineer",
            "tagsandskills": "Coding,Internship",
            "jobdescription": "3+ years of non-internship experience required.",
        }])
        flags = _build_verified_internship_flags(frame.assign(
            _inferred_job_type=["Internship"]
        ))
        self.assertFalse(bool(flags.iloc[0]))

    def test_non_internship_recommendation_outputs_are_unchanged(self):
        cases = [
            (
                "Any",
                {"jobs_analyzed": 267, "jobs_recommended": 56, "excellent_matches": 0, "strong_matches": 5, "fresher_suitable_jobs": 3},
                [
                    "290925926591", "250925921908", "11025011046", "290925501358",
                    "160125015403", "230925506328", "230925918434", "230925507836",
                    "31025909532", "300925010784", "230925027393", "240925012427",
                    "31025003124", "260925928763", "260925023413", "250925009941",
                    "290925018809", "240925929492", "230925506299", "250925914098",
                ],
            ),
            (
                "Full-time",
                {"jobs_analyzed": 4, "jobs_recommended": 1, "excellent_matches": 0, "strong_matches": 0, "fresher_suitable_jobs": 0},
                ["300925020111"],
            ),
        ]

        for job_type, expected_summary, expected_job_ids in cases:
            with self.subTest(job_type=job_type):
                response = self.client.post(
                    "/recommend",
                    json={
                        "role": "Data Analyst",
                        "skills": ["Python", "SQL"],
                        "experience": 0,
                        "location": "Any",
                        "work_mode": "Any",
                        "job_type": job_type,
                    },
                )

                self.assertEqual(response.status_code, 200)
                result = response.json()["results"]
                self.assertEqual(result["summary"], expected_summary)
                self.assertEqual(
                    [item["job_id"] for item in result["recommendations"]],
                    expected_job_ids,
                )
                self.assertEqual(result["limited_skill_overlap_internships"], [])
                self.assertEqual(result["other_relevant_internships"], [])


if __name__ == "__main__":
    unittest.main()