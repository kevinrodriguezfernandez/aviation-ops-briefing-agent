from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: Literal["openai", "huggingface"] = "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    huggingface_api_key: str | None = None

    embedding_provider: Literal["openai", "huggingface"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    openweathermap_api_key: str | None = None
    database_url: str | None = None

    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "ops-briefing-agent"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
