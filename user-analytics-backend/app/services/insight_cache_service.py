"""Cache Gemini report insights to protect free-tier quota."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn.error")

CACHE_TTL_HOURS = 24


def _make_cache_key(
    report_type: str,
    services: list[str],
    period: str,
) -> str:
    raw = f"{report_type}|{'_'.join(sorted(services))}|{period}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def get_cached_insights(
    report_type: str,
    services: list[str],
    period: str,
    db: Session,
) -> dict[str, str] | None:
    cache_key = _make_cache_key(report_type, services, period)

    try:
        row = db.execute(
            text(
                """
                SELECT insights_json, created_at
                FROM report_insights_cache
                WHERE cache_key = :key
                  AND created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"key": cache_key},
        ).fetchone()

        if row and row.insights_json:
            created_at = row.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            logger.info(
                "INSIGHT_CACHE_HIT key=%s age=%s",
                cache_key[:8],
                datetime.now(timezone.utc) - created_at,
            )
            insights = json.loads(row.insights_json)
            insights["__source"] = "cache"
            return insights
    except Exception as exc:
        logger.warning("INSIGHT_CACHE_LOOKUP_FAILED key=%s error=%s", cache_key[:8], exc)
        try:
            db.rollback()
        except Exception:
            pass

    logger.info("INSIGHT_CACHE_MISS key=%s", cache_key[:8])
    return None


def save_insights_to_cache(
    report_type: str,
    services: list[str],
    period: str,
    insights: dict[str, Any],
    db: Session,
) -> None:
    source = insights.get("__source") or insights.get("ai_source")
    if source == "fallback":
        logger.info("INSIGHT_CACHE_SKIP reason=fallback")
        return

    cache_key = _make_cache_key(report_type, services, period)
    payload = {
        key: value
        for key, value in insights.items()
        if key not in {"__source", "ai_source"}
    }

    try:
        db.execute(
            text(
                """
                INSERT INTO report_insights_cache
                    (cache_key, report_type, insights_json, created_at)
                VALUES
                    (:key, :rtype, :json, NOW())
                ON CONFLICT (cache_key)
                DO UPDATE SET
                    report_type = EXCLUDED.report_type,
                    insights_json = EXCLUDED.insights_json,
                    created_at = NOW()
                """
            ),
            {
                "key": cache_key,
                "rtype": report_type,
                "json": json.dumps(payload, ensure_ascii=False),
            },
        )
        db.commit()
        logger.info("INSIGHT_CACHE_SAVED key=%s", cache_key[:8])
    except Exception as exc:
        logger.warning("INSIGHT_CACHE_SAVE_FAILED key=%s error=%s", cache_key[:8], exc)
        try:
            db.rollback()
        except Exception:
            pass
