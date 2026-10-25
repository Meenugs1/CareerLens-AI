import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import requests
from fastapi.testclient import TestClient

from backend import recommendation_service as dataset_service
from backend import market_intelligence_service
from backend import company_intelligence_service
from backend.main import app


class BackendDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_dataset_cache = dataset_service._dataset_cache
        records = []
        role_skills = {
            "Data Analyst": "Python, SQL, Excel",
            "Business Analyst": "SQL, Excel, Power BI",
            "Data Scientist": "Python, SQL, Machine Learning",
        }
        for role, skills in role_skills.items():
            for index in range(6):
                records.append({
                    "title": role,
                    "jobid": f"{role.replace(' ', '-')}-{index}",
                    "currency": "INR",
                    "companyname": "Acme Analytics" if index % 2 == 0 else "Northstar Labs",
                    "tagsandskills": skills,
                    "salary": "12-18 LPA",
                    "location": "Bengaluru",
                    "companyid": f"company-{index % 2}",
                    "reviewscount": 25 + index,
                    "aggregaterating": 4.0,
                    "jobdescription": f"Experience with {skills} is preferred.",
                    "minimumsalary": 1200000,
                    "maximumsalary": 1800000,
                    "minimumexperience": 0,
                    "maximumexperience": 3,
                    "days_ago": index,
                    "salary_available": True,
                    "average_salary": 1500000,
                    "salary_range": "12-18 LPA",
                    "workmode": "Hybrid",
                    "experience": "0-3 years",
                })
        cls.dataset = pd.DataFrame.from_records(records)
        cls.dataset["_inferred_job_type"] = dataset_service._build_inferred_job_types(
            cls.dataset
        )
        cls.dataset["_is_verified_internship"] = (
            dataset_service._build_verified_internship_flags(cls.dataset)
        )
        dataset_service._dataset_cache = cls.dataset
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        dataset_service._dataset_cache = cls.original_dataset_cache

    def test_root_openapi_and_startup(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/openapi.json").status_code, 200)

    def test_startup_failure_keeps_health_and_docs_available(self):
        with patch(
            "backend.main._load_dataset",
            side_effect=dataset_service.DatasetUnavailableError(
                "Dataset unavailable for this test."
            ),
        ), TestClient(app) as client:
            self.assertEqual(client.get("/").status_code, 200)
            self.assertEqual(client.get("/openapi.json").status_code, 200)

    def test_recommendation_integration_returns_ranked_results(self):
        response = self.client.post("/recommend", json={
            "role": "Data Analyst",
            "skills": ["Python", "SQL", "Excel"],
            "experience": 0,
            "location": "Any",
            "work_mode": "Any",
            "job_type": "Any",
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["results"]["summary"]["jobs_analyzed"], 6)
        self.assertEqual(len(payload["results"]["recommendations"]), 6)
        self.assertEqual(
            payload["results"]["recommendations"][0]["matched_skills"],
            ["excel", "python", "sql"],
        )

    def test_invalid_recommendation_request_is_rejected(self):
        response = self.client.post("/recommend", json={"role": "Data Analyst"})
        self.assertEqual(response.status_code, 422)

    def test_all_feature_endpoints_accept_basic_requests(self):
        requests_to_test = [
            ("GET", "/market-intelligence?role=Data%20Analyst", None),
            ("POST", "/skill-gap", {"role": "Data Analyst", "skills": ["Python", "SQL"]}),
            ("POST", "/career-simulator", {"role": "Data Analyst", "skills": ["Python"], "add_skill": "SQL"}),
            ("POST", "/career-switch", {"current_role": "Business Analyst", "current_skills": ["SQL", "Excel"], "target_role": "Data Analyst"}),
            ("GET", "/career-path?role=Data%20Analyst", None),
            ("POST", "/what-can-i-become", {"skills": ["Python", "SQL"]}),
            ("GET", "/companies?query=Acme", None),
            ("GET", "/company-intelligence?company=Acme%20Analytics", None),
        ]
        for method, url, body in requests_to_test:
            with self.subTest(url=url):
                response = self.client.request(method, url, json=body)
                self.assertEqual(response.status_code, 200, response.text)
                self.assertIsInstance(response.json(), dict)

    def test_company_search_empty_query_and_common_name(self):
        empty_response = self.client.get("/companies?query=%20%20")
        self.assertEqual(empty_response.status_code, 200)
        self.assertEqual(empty_response.json()["query"], "")
        self.assertEqual(len(empty_response.json()["companies"]), 2)

        common_response = self.client.get("/companies?query=acme")
        self.assertEqual(common_response.status_code, 200)
        self.assertEqual(common_response.json()["companies"][0]["company"], "Acme Analytics")
        self.assertEqual(common_response.json()["companies"][0]["job_count"], 9)

    def test_company_search_unknown_name_returns_no_matches(self):
        response = self.client.get("/companies?query=NoSuchEmployer")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["companies"], [])

    def test_company_intelligence_reports_missing_salary_and_ratings(self):
        sparse_dataset = self.dataset.iloc[[0]].copy()
        sparse_dataset = sparse_dataset.assign(
            companyname="Sparse Employer",
            currency="USD",
            salary_available=False,
            average_salary=pd.Series([float("nan")], index=sparse_dataset.index),
            salary_range=None,
            aggregaterating=float("nan"),
            reviewscount=float("nan"),
        )
        previous_index = company_intelligence_service._company_index_cache.copy()
        company_intelligence_service._company_index_cache.clear()
        try:
            with patch.object(
                company_intelligence_service,
                "_load_dataset",
                return_value=sparse_dataset,
            ):
                response = self.client.get(
                    "/company-intelligence?company=Sparse%20Employer"
                )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertTrue(payload["success"])
            self.assertFalse(payload["salary"]["available"])
            self.assertFalse(payload["ratings"]["available"])
        finally:
            company_intelligence_service._company_index_cache.clear()
            company_intelligence_service._company_index_cache.update(previous_index)

    def test_concurrent_company_requests_build_index_once(self):
        frame = self.dataset.copy()
        previous_index = company_intelligence_service._company_index_cache.copy()
        company_intelligence_service._company_index_cache.clear()
        original_extract_skills = company_intelligence_service.extract_skills
        count_lock = threading.Lock()
        extraction_count = 0
        start_barrier = threading.Barrier(6)

        def counted_extract_skills(value):
            nonlocal extraction_count
            with count_lock:
                extraction_count += 1
            return original_extract_skills(value)

        def build_index(_):
            start_barrier.wait()
            return company_intelligence_service._build_company_index(frame)

        try:
            with patch.object(
                company_intelligence_service,
                "extract_skills",
                side_effect=counted_extract_skills,
            ):
                with ThreadPoolExecutor(max_workers=6) as executor:
                    indexes = list(executor.map(build_index, range(6)))
            self.assertTrue(all(index is indexes[0] for index in indexes))
            self.assertEqual(extraction_count, len(frame))
        finally:
            company_intelligence_service._company_index_cache.clear()
            company_intelligence_service._company_index_cache.update(previous_index)

    def test_company_index_failure_returns_sanitized_server_error(self):
        original_index = company_intelligence_service._index
        try:
            company_intelligence_service._index = lambda: (_ for _ in ()).throw(
                RuntimeError("private path and secret-value")
            )
            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.get("/companies?query=Acme")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                response.json(),
                {"detail": "The request could not be completed."},
            )
            self.assertNotIn("private path", response.text)
            self.assertNotIn("secret-value", response.text)
        finally:
            company_intelligence_service._index = original_index

    def test_production_cors_preflight(self):
        response = self.client.options(
            "/recommend",
            headers={
                "Origin": "https://career-lens-ai-khaki.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "https://career-lens-ai-khaki.vercel.app",
        )

    def test_dataset_unavailable_response_is_sanitized(self):
        previous_cache = dataset_service._dataset_cache
        dataset_service._dataset_cache = None
        try:
            with tempfile.TemporaryDirectory() as directory:
                missing_file = Path(directory) / "missing.xlsx"
                cache_file = Path(directory) / "cache.pkl"
                denied_response = MagicMock()
                denied_response.status_code = 403
                denied_response.__enter__.return_value = denied_response
                with patch.object(dataset_service, "DATA_FILE", missing_file), patch.object(
                    dataset_service, "CACHE_FILE", cache_file
                ), patch.dict(os.environ, {"HF_TOKEN": "test-only-secret"}), patch.object(
                    dataset_service.requests,
                    "get",
                    return_value=denied_response,
                ):
                    response = self.client.post("/recommend", json={
                        "role": "Data Analyst",
                        "skills": ["Python", "SQL"],
                    })
            self.assertEqual(response.status_code, 503)
            self.assertNotIn("test-only-secret", response.text)
            self.assertNotIn(str(missing_file), response.text)
        finally:
            dataset_service._dataset_cache = previous_cache

    def test_hugging_face_failure_is_sanitized_and_partial_file_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "jobs_cleaned.xlsx"
            with patch.object(dataset_service, "DATA_FILE", data_file), patch.dict(
                os.environ,
                {"HF_TOKEN": "test-only-secret", "HF_DATASET_REPO": "owner/private-data"},
            ), patch.object(
                dataset_service.requests,
                "get",
                side_effect=requests.Timeout("test-only-secret"),
            ):
                with self.assertRaises(dataset_service.DatasetUnavailableError) as raised:
                    dataset_service.ensure_dataset_exists()
            self.assertNotIn("test-only-secret", str(raised.exception))
            self.assertFalse(data_file.exists())
            self.assertFalse(data_file.with_suffix(".xlsx.tmp").exists())

    def test_missing_credentials_report_configuration_without_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "jobs_cleaned.xlsx"
            with patch.object(dataset_service, "DATA_FILE", data_file), patch.dict(
                os.environ,
                {"HF_TOKEN": ""},
            ):
                with self.assertRaises(dataset_service.DatasetUnavailableError) as raised:
                    dataset_service.ensure_dataset_exists()
            self.assertIn("HF_TOKEN", str(raised.exception))
            self.assertNotIn("Bearer", str(raised.exception))

    def test_empty_or_malformed_workbook_is_rejected(self):
        previous_cache = dataset_service._dataset_cache
        dataset_service._dataset_cache = None
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "jobs_cleaned.xlsx"
            cache_file = Path(directory) / "cache.pkl"
            pd.DataFrame({"wrong": ["columns"]}).to_excel(data_file, index=False)
            try:
                with patch.object(dataset_service, "DATA_FILE", data_file), patch.object(
                    dataset_service, "CACHE_FILE", cache_file
                ):
                    with self.assertRaises(dataset_service.DatasetUnavailableError):
                        dataset_service._load_dataset()
                data_file.write_bytes(b"")
                dataset_service._dataset_cache = None
                with patch.object(dataset_service, "DATA_FILE", data_file), patch.object(
                    dataset_service, "CACHE_FILE", cache_file
                ):
                    with self.assertRaises(dataset_service.DatasetUnavailableError):
                        dataset_service._load_dataset()
            finally:
                dataset_service._dataset_cache = previous_cache

    def test_dataset_load_is_cached_after_first_read(self):
        previous_cache = dataset_service._dataset_cache
        dataset_service._dataset_cache = None
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "jobs_cleaned.xlsx"
            cache_file = Path(directory) / "cache.pkl"
            self.dataset.drop(columns=["_inferred_job_type", "_is_verified_internship"]).to_excel(
                data_file,
                index=False,
            )
            original_read_excel = pd.read_excel
            read_count = 0

            def counted_read(*args, **kwargs):
                nonlocal read_count
                read_count += 1
                return original_read_excel(*args, **kwargs)

            try:
                with patch.object(dataset_service, "DATA_FILE", data_file), patch.object(
                    dataset_service, "CACHE_FILE", cache_file
                ), patch.object(dataset_service.pd, "read_excel", side_effect=counted_read):
                    loaded = dataset_service._load_dataset()
                    self.assertIs(dataset_service._load_dataset(), loaded)
                self.assertEqual(read_count, 1)
            finally:
                dataset_service._dataset_cache = previous_cache

    def test_unexpected_errors_do_not_expose_internal_details(self):
        original = market_intelligence_service._load_dataset
        try:
            market_intelligence_service._load_dataset = lambda: (_ for _ in ()).throw(
                RuntimeError("private path and secret-value")
            )
            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.get("/market-intelligence")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                response.json(),
                {"detail": "The request could not be completed."},
            )
            self.assertNotIn("private path", response.text)
            self.assertNotIn("secret-value", response.text)
        finally:
            market_intelligence_service._load_dataset = original


if __name__ == "__main__":
    unittest.main()
