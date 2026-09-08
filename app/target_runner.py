"""Executes the target model against a test-case prompt."""
from app.core.config import get_settings
from app.core.groq_client import get_groq_client
from app.schemas import TestCase


def run_target_model(test_case: TestCase) -> str:
    """Send a test case's prompt to the target model and return its raw response text."""
    settings = get_settings()
    client = get_groq_client()

    response = client.chat.completions.create(
        model=settings.target_model,
        messages=[{"role": "user", "content": test_case.prompt}],
        temperature=settings.target_temperature,
    )
    return response.choices[0].message.content.strip()
