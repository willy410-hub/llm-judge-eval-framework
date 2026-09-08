from unittest.mock import patch

from app.pipeline import run_evaluation_pipeline
from app.schemas import EvaluationResult


def test_run_evaluation_pipeline_produces_one_result_per_test_case(tmp_dataset_file):
    fake_evaluation = EvaluationResult(
        is_correct=True, score=1.0, failure_mode="None", reasoning="ok"
    )

    with patch("app.pipeline.run_target_model", return_value="4"), \
         patch("app.pipeline.evaluate_response", return_value=fake_evaluation):
        results = run_evaluation_pipeline(dataset_path=tmp_dataset_file)

    assert len(results) == 1
    assert results[0].test_case.id == "TC-TEST"
    assert results[0].actual_response == "4"
    assert results[0].evaluation.is_correct is True
