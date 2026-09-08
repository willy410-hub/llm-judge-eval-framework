"""
Centralized configuration.

Model names, the failure taxonomy, and dataset paths live here instead
of being duplicated or implicit across main.py and evaluator/judge.py.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# The full, authoritative failure taxonomy. The original's fallback
# path returned "Pipeline Error" -- a sixth value never declared in the
# judge's own prompt (which only listed five). Declaring it here makes
# it an official category rather than an undocumented escape hatch.
FAILURE_MODES = (
    "None",
    "Factual Hallucination",
    "Logical Fallacy",
    "Schema Mismatch",
    "Over-refusal",
    "Pipeline Error",
)


class Settings(BaseSettings):
    """Runtime configuration, sourced from env vars / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="EVAL_", extra="ignore")

    # --- Groq API ---
    groq_api_key: str = ""

    # --- Models ---
    target_model: str = "llama-3.1-8b-instant"
    judge_model: str = "llama-3.3-70b-versatile"
    target_temperature: float = 0.1
    judge_temperature: float = 0.0

    # --- Dataset ---
    dataset_path: str = "dataset/test_cases.json"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (avoids re-parsing env on every call)."""
    return Settings()
