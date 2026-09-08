import json

import pytest

from app.core.exceptions import DatasetError
from app.dataset_loader import load_test_cases


def test_load_test_cases_returns_validated_models(tmp_dataset_file):
    test_cases = load_test_cases(tmp_dataset_file)

    assert len(test_cases) == 1
    assert test_cases[0].id == "TC-TEST"


def test_load_test_cases_raises_on_missing_file():
    with pytest.raises(DatasetError, match="not found"):
        load_test_cases("dataset/does_not_exist.json")


def test_load_test_cases_raises_on_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(DatasetError, match="not valid JSON"):
        load_test_cases(str(bad_file))


def test_load_test_cases_raises_on_empty_array(tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("[]", encoding="utf-8")

    with pytest.raises(DatasetError, match="non-empty"):
        load_test_cases(str(empty_file))


def test_load_test_cases_raises_on_schema_mismatch(tmp_path):
    bad_shape = tmp_path / "bad_shape.json"
    bad_shape.write_text(json.dumps([{"id": "X"}]), encoding="utf-8")

    with pytest.raises(DatasetError, match="schema validation"):
        load_test_cases(str(bad_shape))


def test_load_test_cases_supports_optional_time_sensitivity_fields(tmp_path):
    data = [
        {
            "id": "TC-TIME",
            "category": "Time-Sensitive Knowledge",
            "prompt": "some prompt",
            "expected_answer": "some answer",
            "as_of_date": "2024-01-01",
            "notes": "may go stale",
        }
    ]
    path = tmp_path / "time_sensitive.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    test_cases = load_test_cases(str(path))

    assert test_cases[0].as_of_date == "2024-01-01"
    assert test_cases[0].notes == "may go stale"


def test_load_test_cases_time_sensitivity_fields_default_to_none(tmp_dataset_file):
    test_cases = load_test_cases(tmp_dataset_file)

    assert test_cases[0].as_of_date is None
    assert test_cases[0].notes is None
