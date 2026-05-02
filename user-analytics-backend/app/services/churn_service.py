"""
Churn Service — agrège les KPIs et charts pour l'API
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.cache import build_cache_key, cache_or_compute
from app.core.config import settings
from app.repositories import churn_repo
from app.utils.temporal import get_default_window

CHURN_DASHBOARD_CACHE_VERSION = "2026-04-16-v2-trial-paid-segmentation"


def get_churn_dashboard(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_id: Optional[str] = None,
) -> dict:
    """Retourne tous les KPIs + données charts pour le dashboard churn."""

    if not start_date or not end_date:
        start_date, end_date = get_default_window(db, days=30, source="billing")

    cache_key = build_cache_key(
        "churn_dashboard",
        {
            "v": CHURN_DASHBOARD_CACHE_VERSION,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "service_id": service_id or "all",
        },
    )

    def _compute_payload() -> dict:
        global_metrics = churn_repo.get_global_churn_rate(db, start_date, end_date, service_id=service_id)
        monthly_metrics = churn_repo.get_monthly_churn_rate(db, start_date, end_date, service_id=service_id)
        trial_vs_paid = churn_repo.get_trial_vs_paid_churn(db, start_date, end_date, service_id=service_id)
        churn_curve = churn_repo.get_churn_curve(db, start_date, end_date, service_id=service_id)
        avg_lifetime_days = churn_repo.get_avg_lifetime_days_filtered(db, start_date, end_date, service_id=service_id)
        churn_breakdown = churn_repo.get_churn_breakdown(db, start_date, end_date, service_id=service_id)

        churn_curve_note = ""
        if len(churn_curve) >= 2:
            max_jump = 0.0
            jump_start = churn_curve[0]["day"]
            jump_end = churn_curve[1]["day"]
            for idx in range(1, len(churn_curve)):
                jump = float(churn_curve[idx]["trial"] or 0) - float(churn_curve[idx - 1]["trial"] or 0)
                if jump > max_jump:
                    max_jump = jump
                    jump_start = churn_curve[idx - 1]["day"]
                    jump_end = churn_curve[idx]["day"]
            if max_jump > 0:
                churn_curve_note = (
                    f"High velocity churn observed in Trial users between Day {jump_start} and {jump_end}."
                )

        return {
            "kpis": {
                "global_churn_rate": {
                    "rate": float(global_metrics.get("global_churn_rate", 0) or 0),
                    "churned": int(global_metrics.get("churned_total", 0) or 0),
                    "total": int(global_metrics.get("total_subscriptions", 0) or 0),
                },
                "monthly_churn_rate": {
                    "rate": float(monthly_metrics.get("rate", 0) or 0),
                    "churned": int(monthly_metrics.get("churned", 0) or 0),
                    "total": int(monthly_metrics.get("total", 0) or 0),
                    "message": monthly_metrics.get("message"),
                },
                "trial_churn": {
                    "rate": float(trial_vs_paid.get("trial_churn_rate", 0) or 0),
                    "count": int(trial_vs_paid.get("total_churned", 0) or 0),
                },
                "avg_lifetime_days": {
                    "avg_days": float(avg_lifetime_days or 0),
                    "min_days": 0,
                },
                "churn_breakdown": churn_breakdown,
            },
            "charts": {
                "daily_trend": churn_repo.get_churn_trend_daily(db, start_date, end_date, service_id=service_id),
                "churn_curve": churn_curve,
                "churn_curve_note": churn_curve_note,
                "by_service": churn_repo.get_churn_by_service(db, start_date, end_date, service_id=service_id),
                "lifetime_distribution": churn_repo.get_lifetime_distribution(db, start_date, end_date, service_id=service_id),
                "retention_cohort": churn_repo.get_retention_cohort(db, start_date, end_date, service_id=service_id),
            },
            "meta": {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "data_source": "analytics_db",
            },
        }

    return cache_or_compute(
        cache_key,
        settings.CHURN_CACHE_TTL_SECONDS,
        compute_function=_compute_payload,
    )