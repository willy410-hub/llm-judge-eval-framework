"""Orchestrates the full evaluation pipeline: load -> execute -> judge."""
from app.core.config import get_settings
from app.dataset_loader import load_test_cases
from app.judge import evaluate_response
from app.schemas import CaseOutcome
from app.target_runner import run_target_model


def run_evaluation_pipeline(dataset_path: str | None = None) -> list[CaseOutcome]:
    """
    Run every test case in the dataset through the target model and the
    judge, returning the full list of results.
    """
    settings = get_settings()
    path = dataset_path or settings.dataset_path

    test_cases = load_test_cases(path)
    results: list[CaseOutcome] = []

    for test_case in test_cases:
        actual_response = run_target_model(test_case)
        evaluation = evaluate_response(test_case, actual_response)
        results.append(
            CaseOutcome(
                test_case=test_case, actual_response=actual_response, evaluation=evaluation
            )
        )

    return results
