# app/core/config.py

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings for API + Alembic.

    Accept both legacy and current env names:
    - DATABASE_URL
    - ANALYTICS_CONN / analytics_conn
    """

    DATABASE_URL: str | None = None
    ANALYTICS_CONN: str | None = Field(default=None, alias="ANALYTICS_CONN")
    analytics_conn: str | None = None
    HAWALA_CONN: str | None = Field(default=None, alias="HAWALA_CONN")
    hawala_conn: str | None = None
    REDIS_URL: str = "redis://localhost:6379/0"
    ANALYTICS_CACHE_TTL_SECONDS: int = 3600
    OVERVIEW_CACHE_TTL_SECONDS: int = 60
    TRIAL_KPIS_CACHE_TTL_SECONDS: int = 90
    CROSS_SERVICE_CACHE_TTL_SECONDS: int = 180
    RETENTION_CACHE_TTL_SECONDS: int = 300
    USER_ACTIVITY_CACHE_TTL_SECONDS: int = 30
    ML_SCORES_CACHE_TTL_SECONDS: int = 300
    CACHE_LOCK_TTL_SECONDS: int = 30
    CACHE_LOCK_WAIT_MS: int = 1200
    CACHE_LOCK_POLL_INTERVAL_MS: int = 80

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # Ignore unrelated env vars during Alembic startup
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def _normalize_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.ANALYTICS_CONN or self.analytics_conn
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL (or ANALYTICS_CONN) is required")
        return self


settings = Settings()
