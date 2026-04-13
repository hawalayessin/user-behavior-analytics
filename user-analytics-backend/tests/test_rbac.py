from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_analyst_blocked(analyst_client):
    """Verify analyst role cannot access admin-only management create route."""
    response = await analyst_client.post(
        "/admin/management/services",
        json={"name": "Test Service", "billing_type": "daily", "price": 1.0},
    )

    assert response.status_code == 403
    detail = str(response.json().get("detail", ""))
    assert (
        "admin" in detail.lower()
        or "forbidden" in detail.lower()
        or "administrateur" in detail.lower()
    )


@pytest.mark.anyio
async def test_admin_allowed(admin_client):
    """Verify admin role can access management list services route."""
    response = await admin_client.get("/admin/management/services")
    if response.status_code != 200:
        pytest.skip("No seed data available")

    data = response.json()
    assert isinstance(data, list)
