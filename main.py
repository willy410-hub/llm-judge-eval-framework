"""CLI entrypoint: run the full evaluation pipeline and print a report."""
from app.core.config import get_settings
from app.core.exceptions import EvalFrameworkError
from app.pipeline import run_evaluation_pipeline
from app.report import print_report


def main() -> None:
    settings = get_settings()

    print(f"Starting Evaluation Pipeline against Target Model: {settings.target_model}\n")

    try:
        results = run_evaluation_pipeline()
    except EvalFrameworkError as exc:
        print(f"Error: {exc}")
        return

    for result in results:
        status = "PASS" if result.evaluation.is_correct else "FAIL"
        print(f"[{result.test_case.id}] {result.test_case.category}: {status}")

    print_report(results)


if __name__ == "__main__":
    main()
