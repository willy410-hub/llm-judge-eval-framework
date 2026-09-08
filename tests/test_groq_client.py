import pytest

from app.core.exceptions import MissingAPIKeyError


def test_get_groq_client_raises_clean_error_without_api_key(monkeypatch):
    from app.core.config import get_settings
    from app.core.groq_client import get_groq_client

    get_settings.cache_clear()
    monkeypatch.delenv("EVAL_GROQ_API_KEY", raising=False)

    import app.core.groq_client as groq_client_module

    groq_client_module._client = None

    with pytest.raises(MissingAPIKeyError):
        get_groq_client()
