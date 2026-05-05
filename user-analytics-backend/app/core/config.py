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
    PROD_CONN: str | None = Field(default=None, alias="PROD_CONN")
    prod_conn: str | None = None
    REDIS_URL: str = "redis://localhost:6379/0"
    ANALYTICS_CACHE_TTL_SECONDS: int = 86400
    OVERVIEW_CACHE_TTL_SECONDS: int = 86400
    TRIAL_KPIS_CACHE_TTL_SECONDS: int = 86400
    CROSS_SERVICE_CACHE_TTL_SECONDS: int = 86400
    CROSS_SERVICE_DEFAULT_WINDOW_DAYS: int = 365
    RETENTION_CACHE_TTL_SECONDS: int = 86400
    CHURN_CACHE_TTL_SECONDS: int = 86400
    USER_ACTIVITY_CACHE_TTL_SECONDS: int = 86400
    SEGMENTATION_CACHE_TTL_SECONDS: int = 86400
    CAMPAIGN_CACHE_TTL_SECONDS: int = 86400
    ML_SCORES_CACHE_TTL_SECONDS: int = 86400
    ML_METRICS_CACHE_TTL_SECONDS: int = 86400
    SEGMENTATION_SQL_TIMEOUT_MS: int = 180000
    CACHE_LOCK_TTL_SECONDS: int = 30
    CACHE_LOCK_WAIT_MS: int = 1200
    CACHE_LOCK_POLL_INTERVAL_MS: int = 80

    # SMTP Configuration for password reset emails
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "noreply@digmaco.tn"
    SMTP_USE_TLS: bool = True
    FRONTEND_BASE_URL: str = "http://localhost:5173"

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
