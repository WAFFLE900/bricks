from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bricks API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 30
    database_url: str
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    web_base_url: str = "http://localhost:5173"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    facebook_client_id: str = ""
    facebook_client_secret: str = ""
    facebook_redirect_uri: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_database_url(self) -> "Settings":
        database_url = self.database_url.strip()
        if not database_url:
            raise ValueError("DATABASE_URL must be set.")

        postgres_prefixes = ("postgresql://", "postgresql+psycopg://")
        if database_url.startswith(postgres_prefixes):
            return self

        if self.app_env.lower() in {"test", "testing"}:
            return self

        raise ValueError(
            "DATABASE_URL must use PostgreSQL in this environment "
            "(expected prefix: postgresql:// or postgresql+psycopg://)."
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
