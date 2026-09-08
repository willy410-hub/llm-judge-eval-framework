"""Test-case dataset loading and validation."""
import json
from pathlib import Path

from app.core.exceptions import DatasetError
from app.schemas import TestCase


def load_test_cases(dataset_path: str) -> list[TestCase]:
    """
    Load and validate the test-case dataset from a JSON file.

    Raises DatasetError if the file is missing, isn't valid JSON, or
    doesn't match the TestCase schema.
    """
    path = Path(dataset_path)
    if not path.exists():
        raise DatasetError(f"Dataset not found at '{dataset_path}'.")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DatasetError(f"Dataset at '{dataset_path}' is not valid JSON.") from exc

    if not isinstance(raw, list) or not raw:
        raise DatasetError("Dataset must be a non-empty JSON array.")

    try:
        return [TestCase.model_validate(item) for item in raw]
    except Exception as exc:  # pydantic ValidationError
        raise DatasetError(f"Dataset failed schema validation: {exc}") from exc
