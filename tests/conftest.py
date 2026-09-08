"""Shared pytest fixtures."""
import json

import pytest

from app.schemas import TestCase


@pytest.fixture
def sample_test_case() -> TestCase:
    return TestCase(
        id="TC-TEST",
        category="Test Category",
        prompt="What is 2 + 2?",
        expected_answer="4",
    )


@pytest.fixture
def sample_time_sensitive_test_case() -> TestCase:
    return TestCase(
        id="TC-TIME",
        category="Time-Sensitive Knowledge",
        prompt="How many moons does Jupiter have?",
        expected_answer="95 moons",
        as_of_date="2024-03-01",
        notes="Count changes over time.",
    )


@pytest.fixture
def tmp_dataset_file(tmp_path, sample_test_case):
    data = [json.loads(sample_test_case.model_dump_json())]
    path = tmp_path / "test_cases.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)
