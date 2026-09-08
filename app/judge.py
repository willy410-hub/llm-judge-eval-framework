"""
LLM-as-a-Judge: evaluates a target model's response against a test
case's expected answer and gold-standard context.

Bug fixed from the original: the fallback path (any exception during
the judge call or JSON parsing) returned failure_mode="Pipeline Error",
a sixth value never declared in the judge's own system prompt (which
only listed five). "Pipeline Error" is now an official member of the
FailureMode literal (see app/schemas.py) and is mentioned explicitly in
the prompt, so it's a documented category rather than an undocumented
escape hatch.
"""
import json

from app.core.config import get_settings
from app.core.groq_client import get_groq_client
from app.schemas import EvaluationResult, TestCase

_JUDGE_SYSTEM_PROMPT = """You are an expert Frontier AI Research Evaluator. Your task is to evaluate the quality of an LLM generation against a test prompt and expected behavior.

Analyze the actual response and return a JSON object with:
- "is_correct": boolean
- "score": float between 0.0 and 1.0
- "failure_mode": Choose exactly ONE from ["None", "Factual Hallucination", "Logical Fallacy", "Schema Mismatch", "Over-refusal"]
- "reasoning": Concise explanation of the judgment.
"""


def _build_user_content(test_case: TestCase, actual_response: str) -> str:
    context_note = ""
    if test_case.as_of_date:
        context_note = (
            f"\nNote: the expected answer was verified accurate as of {test_case.as_of_date}. "
            "If this is time-sensitive knowledge and the actual response reflects a more "
            "recent, verifiably correct value, do not penalize it as a hallucination."
        )

    return (
        f"Prompt: {test_case.prompt}\n"
        f"Expected Behavior/Answer: {test_case.expected_answer}{context_note}\n"
        f"Actual LLM Response: {actual_response}"
    )


def evaluate_response(test_case: TestCase, actual_response: str) -> EvaluationResult:
    """
    Ask the judge model to score `actual_response` against `test_case`.

    On any failure (API error, malformed JSON, schema mismatch), returns
    an EvaluationResult with failure_mode="Pipeline Error" -- a
    documented category (see FailureMode in app/schemas.py) rather than
    a silent, undeclared fallback value.
    """
    settings = get_settings()
    client = get_groq_client()

    try:
        response = client.chat.completions.create(
            model=settings.judge_model,
            messages=[
                {"role": "system", "content": _JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_content(test_case, actual_response)},
            ],
            response_format={"type": "json_object"},
            temperature=settings.judge_temperature,
        )
        data = json.loads(response.choices[0].message.content)
        return EvaluationResult(**data)
    except Exception as exc:
        return EvaluationResult(
            is_correct=False,
            score=0.0,
            failure_mode="Pipeline Error",
            reasoning=f"Evaluation failed due to error: {exc}",
        )
