"""
Shared Groq client factory.

The original constructed two separate Groq client instances -- one in
main.py for the target model, one inside LLMJudge for the judge model
-- each independently reading the API key. Both now share this one
lazily-constructed client.
"""
from app.core.config import get_settings
from app.core.exceptions import MissingAPIKeyError

_client = None


def get_groq_client():
    """Return a lazily-constructed, module-level Groq client."""
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.groq_api_key:
            raise MissingAPIKeyError()

        from groq import Groq

        _client = Groq(api_key=settings.groq_api_key)
    return _client
