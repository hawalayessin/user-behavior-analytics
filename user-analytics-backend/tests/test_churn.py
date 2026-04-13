from __future__ import annotations

import pytest

from app.routers import churn_analysis as churn_router
from app.routers import ml_churn as ml_router


@pytest.mark.anyio
async def test_churn_kpis(analyst_client, monkeypatch):
    """Verify churn KPIs endpoint returns a valid, non-negative KPI structure."""

    monkeypatch.setattr(churn_router, "_kpi_global_churn_rate", lambda: {"rate": 6.2, "churned": 62, "total": 1000})
    monkeypatch.setattr(churn_router, "_kpi_monthly_churn_rate", lambda: {"rate": 4.1, "churned": 18, "total": 440})
    monkeypatch.setattr(churn_router, "_kpi_avg_lifetime_days", lambda: {"avg_days": 46})
    monkeypatch.setattr(
        churn_router,
        "_kpi_churn_breakdown",
        lambda: {
            "total": 18,
            "voluntary": {"count": 10, "rate": 55.6},
            "technical": {"count": 8, "rate": 44.4},
        },
    )

    response = await analyst_client.get("/analytics/churn/kpis")
    assert response.status_code == 200

    data = response.json()
    churn_rate = data.get("churn_rate")
    churned_users = data.get("churned_users")

    if churn_rate is None:
        churn_rate = (data.get("monthly_churn_rate") or {}).get("rate")
    if churned_users is None:
        churned_users = (data.get("monthly_churn_rate") or {}).get("churned", 0)

    assert isinstance(churn_rate, (int, float))
    assert churned_users >= 0


@pytest.mark.anyio
async def test_ml_churn_scores(analyst_client, monkeypatch):
    """Verify ML churn scores endpoint returns risky users structure with risk values."""

    monkeypatch.setattr(ml_router, "cache_or_compute", lambda _key, _ttl, compute_function: compute_function())
    monkeypatch.setattr(
        ml_router,
        "_compute_churn_scores",
        lambda db, top, threshold, store, use_cached: {
            "generated_at": "2026-04-10T00:00:00+00:00",
            "threshold": threshold,
            "distribution": [
                {"risk_category": "Low", "count": 1},
                {"risk_category": "Medium", "count": 1},
                {"risk_category": "High", "count": 1},
            ],
            "top_users": [
                {
                    "user_id": "00000000-0000-0000-0000-000000000001",
                    "phone_number": "+21600000000",
                    "service_name": "SMS",
                    "churn_risk": 0.92,
                    "risk_category": "High",
                    "predicted_churn": 1,
                }
            ],
            "active_users_scored": 3,
        },
    )

    response = await analyst_client.get("/ml/churn/scores")
    assert response.status_code == 200

    data = response.json()
    if isinstance(data, list):
        assert len(data) > 0
        first = data[0]
    else:
        assert "top_users" in data or "scores" in data
        users = data.get("top_users") or data.get("scores") or []
        if not users:
            pytest.skip("No seed data available")
        first = users[0]

    assert (
        "churn_probability" in first
        or "risk_score" in first
        or "churn_risk" in first
    )
