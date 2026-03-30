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
