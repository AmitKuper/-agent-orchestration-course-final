"""Application settings loaded from environment variables and .env file.

All configurable values live here — nothing is hard-coded in route handlers.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment / .env."""

    database_url: str = "sqlite+aiosqlite:///./cop_thief.db"
    secret_key: str = "change-me-in-production"
    server_name: str = "cop-thief-server"
    allowed_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"

    # LLM gatekeeper — key comes from env, never hard-coded
    anthropic_api_key: str = ""

    # Email delivery — empty string disables sending
    email_recipient: str = ""
    email_smtp_host: str = ""
    email_smtp_port: int = 587
    email_smtp_user: str = ""
    email_smtp_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton."""
    return Settings()
