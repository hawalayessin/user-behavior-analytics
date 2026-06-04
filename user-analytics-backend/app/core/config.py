# app/core/config.py

import os
from urllib.parse import urlparse, urlunparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _running_in_docker() -> bool:
    """Best-effort Docker detection for local-vs-container DB host normalization."""
    return os.path.exists("/.dockerenv")


def _normalize_host_for_runtime(url: str) -> str:
    """Map Docker-only and host-only names so the same env works locally and in containers."""
    parsed = urlparse(url)
    if parsed.hostname == "host.docker.internal" and not _running_in_docker():
        netloc = parsed.netloc.replace("host.docker.internal", "localhost", 1)
        return urlunparse(parsed._replace(netloc=netloc))

    if parsed.hostname == "analytics_redis" and not _running_in_docker():
        netloc = parsed.netloc.replace("analytics_redis", "localhost", 1)
        return urlunparse(parsed._replace(netloc=netloc))

    if parsed.hostname == "localhost" and _running_in_docker():
        netloc = parsed.netloc.replace("localhost", "host.docker.internal", 1)
        return urlunparse(parsed._replace(netloc=netloc))

    return url


def _normalize_db_host_for_runtime(url: str) -> str:
    """When running on host OS, map Docker-internal DB hostnames to localhost."""
    parsed = urlparse(url)
    if parsed.hostname != "host.docker.internal" or _running_in_docker():
        return url

    if parsed.port is None:
        return url

    netloc = parsed.netloc.replace("host.docker.internal", "localhost", 1)
    return urlunparse(parsed._replace(netloc=netloc))


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
    ANOMALY_DAILY_METRICS_CACHE_TTL_SECONDS: int = 86400
    ANOMALY_RESULTS_CACHE_TTL_SECONDS: int = 86400
    ANOMALY_MOST_AFFECTED_CACHE_TTL_SECONDS: int = 86400
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
    SMTP_STRICT_DELIVERY: bool = False
    FRONTEND_BASE_URL: str = "http://localhost:5173"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    REPORTS_OUTPUT_DIR: str = os.getenv("REPORTS_OUTPUT_DIR", "reports/generated")

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
        self.DATABASE_URL = _normalize_db_host_for_runtime(self.DATABASE_URL)
        self.REDIS_URL = _normalize_host_for_runtime(self.REDIS_URL)
        return self


settings = Settings()
