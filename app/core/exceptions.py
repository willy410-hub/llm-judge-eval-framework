"""Domain-specific exceptions."""


class EvalFrameworkError(Exception):
    """Base class for all evaluation-framework errors."""


class MissingAPIKeyError(EvalFrameworkError):
    """Raised when GROQ_API_KEY is not configured."""

    def __init__(self):
        super().__init__(
            "EVAL_GROQ_API_KEY is not set. Copy .env.example to .env and add your Groq key."
        )


class DatasetError(EvalFrameworkError):
    """Raised when the test-case dataset is missing or malformed."""
