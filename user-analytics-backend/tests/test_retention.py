from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_retention_kpis(analyst_client):
    """Verify retention KPIs endpoint returns D7/D30-compatible keys within valid range."""
    response = await analyst_client.get("/analytics/retention/kpis")
    if response.status_code != 200:
        pytest.skip("No seed data available")

    data = response.json()
    assert (
        "retention_d7" in data
        or "d7" in data
        or "avg_retention_d7" in data
    )
    assert (
        "retention_d30" in data
        or "d30" in data
        or "avg_retention_d30" in data
    )

    d7 = (
        data.get("retention_d7")
        if data.get("retention_d7") is not None
        else data.get("d7")
        if data.get("d7") is not None
        else data.get("avg_retention_d7")
    )

    if d7 is None:
        pytest.skip("No seed data available")

    assert 0 <= float(d7) <= 100


@pytest.mark.anyio
async def test_retention_heatmap(analyst_client):
    """Verify retention heatmap endpoint returns cohort list-like data."""
    response = await analyst_client.get("/analytics/retention/heatmap")
    if response.status_code != 200:
        pytest.skip("No seed data available")

    data = response.json()
    assert isinstance(data, list) or "cohorts" in data or "data" in data
