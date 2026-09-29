from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CircleSpace API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./social.db"
    secret_key: str = "development-secret-change-me-at-least-32-bytes"
    access_token_expire_minutes: int = 1_440
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout_seconds: int = 30
    backend_cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",")]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
