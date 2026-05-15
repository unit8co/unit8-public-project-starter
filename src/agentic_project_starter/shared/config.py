"""Typed application settings shared by API, CLI, and starter services."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "docker", "ci"]


class Settings(BaseSettings):
    """Application settings loaded from `.env` files and process environment."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "agentic-project-starter"
    app_environment: EnvironmentName = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    openai_api_key: str | None = None
    openai_model: str = "gpt-5"
    openai_default_agent: str = "coordinator"
    openai_enable_tracing: bool = False
    chatkit_domain_key: str = "local-dev"

    storage_uri: str = "file://./var/data"
    etl_default_dataset: str = "demo-dataset"
    otel_exporter_otlp_endpoint: str | None = None

    api_base_path: str = Field(default="/v1", pattern=r"^/")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance for the active process."""

    return Settings()
