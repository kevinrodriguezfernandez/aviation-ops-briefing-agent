from src.core.config import Settings, get_settings


def test_settings_reads_values_from_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LLM_PROVIDER=huggingface",
                "LLM_MODEL=test-llm",
                "OPENAI_API_KEY=test-openai",
                "HUGGINGFACE_API_KEY=test-hf",
                "EMBEDDING_PROVIDER=huggingface",
                "EMBEDDING_MODEL=test-embedding",
                "EMBEDDING_DIMENSION=42",
                "OPENWEATHERMAP_API_KEY=test-weather",
                "DATABASE_URL=postgresql+asyncpg://ops:ops_test@localhost:5432/ops_briefing_test",
                "LANGCHAIN_TRACING_V2=true",
                "LANGCHAIN_API_KEY=test-langsmith",
                "LANGCHAIN_PROJECT=test-project",
                "LOG_LEVEL=DEBUG",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.llm_provider == "huggingface"
    assert settings.llm_model == "test-llm"
    assert settings.openai_api_key == "test-openai"
    assert settings.huggingface_api_key == "test-hf"
    assert settings.embedding_provider == "huggingface"
    assert settings.embedding_model == "test-embedding"
    assert settings.embedding_dimension == 42
    assert settings.openweathermap_api_key == "test-weather"
    assert settings.database_url == "postgresql+asyncpg://ops:ops_test@localhost:5432/ops_briefing_test"
    assert settings.langchain_tracing_v2 is True
    assert settings.langchain_api_key == "test-langsmith"
    assert settings.langchain_project == "test-project"
    assert settings.log_level == "DEBUG"


def test_get_settings_is_cached(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=postgresql+asyncpg://cached\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second
