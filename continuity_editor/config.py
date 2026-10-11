"""Project settings, loaded from the `.env` file at the repository root.

Neo4j and the LLM have separate settings, so either can be used without the other.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


class _EnvFileSettings(BaseSettings):
    # An absolute path, so notebooks running from notebooks/ still find the file.
    # extra="ignore" lets you paste the whole AuraDB credentials file into .env.
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")


class Neo4jSettings(_EnvFileSettings):
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: SecretStr
    neo4j_database: str | None = None  # None = the instance's default database


class LLMSettings(_EnvFileSettings):
    """Local LLM served by Ollama: free, runs on this computer, no account or API key."""

    ollama_host: str = "http://localhost:11434"
    # Small enough for an 8 GB Mac. Use the same model everywhere when comparing results.
    llm_model: str = "qwen3:4b-instruct"
    # Ollama's num_ctx. Input longer than this is silently cut off, so chapters are sent
    # in chunks that fit. Raising it needs more memory.
    llm_context_tokens: int = 8192
    # For "thinking" models such as qwen3:14b, False makes them answer directly (faster).
    # Leave unset for models without thinking, such as qwen3:4b-instruct.
    llm_think: bool | None = None


@lru_cache
def get_neo4j_settings() -> Neo4jSettings:
    try:
        return Neo4jSettings()
    except ValidationError as exc:
        missing = sorted(str(err["loc"][0]).upper() for err in exc.errors() if err["type"] == "missing")
        if missing:
            raise RuntimeError(
                f"Missing setting(s): {', '.join(missing)}. "
                f"Copy .env.example to {ENV_FILE} and fill them in."
            ) from exc
        raise


@lru_cache
def get_llm_settings() -> LLMSettings:
    return LLMSettings()
