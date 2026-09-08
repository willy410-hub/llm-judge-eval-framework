"""Formats a list of CaseOutcome objects into a printable report."""
from app.schemas import CaseOutcome

_HEADERS = ["ID", "Category", "Status", "Score", "Failure Mode", "Judge Reasoning Snippet"]


def build_report_rows(results: list[CaseOutcome]) -> list[list[str]]:
    """Convert results into tabulate-ready rows."""
    rows = []
    for result in results:
        status = "PASS" if result.evaluation.is_correct else "FAIL"
        snippet = result.evaluation.reasoning[:60] + "..."
        rows.append([
            result.test_case.id,
            result.test_case.category,
            status,
            f"{result.evaluation.score:.2f}",
            result.evaluation.failure_mode,
            snippet,
        ])
    return rows


def print_report(results: list[CaseOutcome]) -> None:
    """Print a formatted evaluation report to stdout."""
    from tabulate import tabulate

    print("\n" + "=" * 80)
    print("EVALUATION & FAILURE ANALYSIS REPORT")
    print("=" * 80)
    print(tabulate(build_report_rows(results), headers=_HEADERS, tablefmt="grid"))
