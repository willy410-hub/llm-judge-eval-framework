import json
from unittest.mock import MagicMock, patch

from app.judge import evaluate_response


def _mock_groq_response(payload: dict):
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = json.dumps(payload)
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )
    return mock_client


def test_evaluate_response_returns_parsed_result(sample_test_case):
    payload = {
        "is_correct": True,
        "score": 1.0,
        "failure_mode": "None",
        "reasoning": "Correct answer.",
    }
    with patch("app.judge.get_groq_client", return_value=_mock_groq_response(payload)):
        result = evaluate_response(sample_test_case, "4")

    assert result.is_correct is True
    assert result.score == 1.0
    assert result.failure_mode == "None"


def test_evaluate_response_falls_back_to_pipeline_error_on_bad_json(sample_test_case):
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "{not valid json"
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )

    with patch("app.judge.get_groq_client", return_value=mock_client):
        result = evaluate_response(sample_test_case, "4")

    assert result.failure_mode == "Pipeline Error"
    assert result.is_correct is False
    assert result.score == 0.0


def test_evaluate_response_falls_back_to_pipeline_error_on_api_exception(sample_test_case):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("API down")

    with patch("app.judge.get_groq_client", return_value=mock_client):
        result = evaluate_response(sample_test_case, "4")

    assert result.failure_mode == "Pipeline Error"
    assert "API down" in result.reasoning


def test_evaluate_response_falls_back_on_invalid_failure_mode_value(sample_test_case):
    """The judge model could hallucinate a failure_mode value outside the
    declared literal -- Pydantic validation should reject it and the
    call site falls back to the documented Pipeline Error path."""
    payload = {
        "is_correct": False,
        "score": 0.0,
        "failure_mode": "Something Undeclared",
        "reasoning": "test",
    }
    with patch("app.judge.get_groq_client", return_value=_mock_groq_response(payload)):
        result = evaluate_response(sample_test_case, "4")

    assert result.failure_mode == "Pipeline Error"


def test_evaluate_response_includes_as_of_date_context_for_time_sensitive_cases(
    sample_time_sensitive_test_case,
):
    payload = {
        "is_correct": True,
        "score": 1.0,
        "failure_mode": "None",
        "reasoning": "ok",
    }
    mock_client = _mock_groq_response(payload)

    with patch("app.judge.get_groq_client", return_value=mock_client):
        evaluate_response(sample_time_sensitive_test_case, "97 moons")

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    user_message = call_kwargs["messages"][1]["content"]
    assert "2024-03-01" in user_message
    assert "do not penalize" in user_message.lower()
