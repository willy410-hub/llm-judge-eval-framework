from unittest.mock import MagicMock, patch

from app.target_runner import run_target_model


def test_run_target_model_returns_stripped_response(sample_test_case):
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "  4  \n"
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )

    with patch("app.target_runner.get_groq_client", return_value=mock_client):
        result = run_target_model(sample_test_case)

    assert result == "4"


def test_run_target_model_sends_the_test_case_prompt(sample_test_case):
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "response"
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=mock_message)]
    )

    with patch("app.target_runner.get_groq_client", return_value=mock_client):
        run_target_model(sample_test_case)

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["messages"][0]["content"] == sample_test_case.prompt
