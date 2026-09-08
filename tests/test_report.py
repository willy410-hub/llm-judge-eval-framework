from app.report import build_report_rows
from app.schemas import CaseOutcome, EvaluationResult


def test_build_report_rows_formats_pass_status(sample_test_case):
    result = CaseOutcome(
        test_case=sample_test_case,
        actual_response="4",
        evaluation=EvaluationResult(
            is_correct=True, score=1.0, failure_mode="None", reasoning="Correct."
        ),
    )

    rows = build_report_rows([result])

    assert rows[0][2] == "PASS"
    assert rows[0][3] == "1.00"


def test_build_report_rows_formats_fail_status(sample_test_case):
    result = CaseOutcome(
        test_case=sample_test_case,
        actual_response="5",
        evaluation=EvaluationResult(
            is_correct=False,
            score=0.0,
            failure_mode="Factual Hallucination",
            reasoning="Wrong answer given by the model.",
        ),
    )

    rows = build_report_rows([result])

    assert rows[0][2] == "FAIL"
    assert rows[0][4] == "Factual Hallucination"


def test_build_report_rows_truncates_long_reasoning(sample_test_case):
    long_reasoning = "x" * 200
    result = CaseOutcome(
        test_case=sample_test_case,
        actual_response="4",
        evaluation=EvaluationResult(
            is_correct=True, score=1.0, failure_mode="None", reasoning=long_reasoning
        ),
    )

    rows = build_report_rows([result])

    assert len(rows[0][5]) < len(long_reasoning)
    assert rows[0][5].endswith("...")
