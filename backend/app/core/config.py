from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QueryPilot"
    app_env: str = "local"
    application_database_url: str = (
        "postgresql+psycopg://querypilot_app:querypilot_app@postgres:5432/querypilot"
    )
    generated_query_database_url: str = (
        "postgresql+psycopg://querypilot_reader:querypilot_reader@postgres:5432/querypilot"
    )
    generated_query_timeout_ms: int = Field(default=5_000, ge=100, le=30_000)
    generated_query_max_rows: int = Field(default=200, ge=1, le=1_000)
    query_provider: str = "demo"
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_base_url: str | None = None
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
