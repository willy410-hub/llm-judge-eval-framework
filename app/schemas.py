"""Pydantic data contracts."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

FailureMode = Literal[
    "None",
    "Factual Hallucination",
    "Logical Fallacy",
    "Schema Mismatch",
    "Over-refusal",
    "Pipeline Error",
]


class TestCase(BaseModel):
    """A single evaluation test case."""

    id: str
    category: str
    prompt: str
    expected_answer: str
    as_of_date: Optional[str] = Field(
        None,
        description=(
            "For time-sensitive test cases: the date this expected_answer was "
            "verified accurate. Signals that the gold standard may go stale."
        ),
    )
    notes: Optional[str] = Field(
        None, description="Free-form context, e.g. why the expected answer may change over time."
    )


class EvaluationResult(BaseModel):
    """A judge's verdict on one target-model response."""

    is_correct: bool
    score: float = Field(ge=0.0, le=1.0)
    failure_mode: FailureMode
    reasoning: str


class CaseOutcome(BaseModel):
    """One test case's full outcome: the target's response plus the judge's verdict."""

    test_case: TestCase
    actual_response: str
    evaluation: EvaluationResult
