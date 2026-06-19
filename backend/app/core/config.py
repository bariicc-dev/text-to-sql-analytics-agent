from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QueryPilot"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/querypilot"
    query_provider: str = "demo"
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_base_url: str | None = None
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
