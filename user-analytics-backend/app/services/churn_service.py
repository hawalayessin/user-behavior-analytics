"""
Churn Service — agrège les KPIs et charts pour l'API
"""
from datetime import datetime
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories import churn_repo
from app.utils.temporal import get_month_window


_DASHBOARD_CACHE_TTL_SECONDS = 30
_dashboard_cache: dict[tuple[str, str], tuple[float, dict]] = {}


def get_churn_dashboard(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """Retourne tous les KPIs + données charts pour le dashboard churn."""

    if not start_date or not end_date:
        start_date, end_date = get_month_window(db)

    cache_key = (start_date.isoformat(), end_date.isoformat())
    cached = _dashboard_cache.get(cache_key)
    now = time.monotonic()
    if cached and now - cached[0] < _DASHBOARD_CACHE_TTL_SECONDS:
        return cached[1]

    global_metrics = churn_repo.get_global_churn_rate(db, start_date, end_date)
    avg_lifetime_days = churn_repo.get_avg_lifetime_days(db, start_date, end_date)
    churn_breakdown = churn_repo.get_churn_breakdown(db, start_date, end_date)

    payload = {
        "kpis": {
            "global_churn_rate": {
                "rate": float(global_metrics.get("global_churn_rate", 0) or 0),
                "churned": int(global_metrics.get("churned_total", 0) or 0),
                "total": int(global_metrics.get("total_subscriptions", 0) or 0),
            },
            "monthly_churn_rate": {
                "rate": float(global_metrics.get("monthly_churn_rate", 0) or 0),
                "churned": int(global_metrics.get("period_churned", 0) or 0),
                "total": int(global_metrics.get("total_subscriptions", 0) or 0),
            },
            "avg_lifetime_days": {
                "avg_days": float(avg_lifetime_days or 0),
                "min_days": 0,
            },
            "churn_breakdown": churn_breakdown,
        },
        "charts": {
            "daily_trend": churn_repo.get_churn_trend_daily(db, start_date, end_date),
            "by_service": churn_repo.get_churn_by_service(db, start_date, end_date),
            "lifetime_distribution": churn_repo.get_lifetime_distribution(db, start_date, end_date),
            "retention_cohort": churn_repo.get_retention_cohort(db, start_date, end_date),
        },
        "meta": {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "data_source": "analytics_db",
        },
    }

    _dashboard_cache[cache_key] = (now, payload)
    return payload