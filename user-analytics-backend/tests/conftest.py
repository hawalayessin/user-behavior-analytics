from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_user
from app.main import app
from app.models.platform_users import PlatformUser


def _mock_user(*, role: str, email: str) -> PlatformUser:
    return PlatformUser(
        id=uuid.uuid4(),
        email=email,
        password_hash="test_hash",
        full_name=f"test_{role}",
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


def mock_admin() -> PlatformUser:
    return _mock_user(role="admin", email="test_admin@example.com")


def mock_analyst() -> PlatformUser:
    return _mock_user(role="analyst", email="test_analyst@example.com")


@pytest.fixture
async def admin_client():
    app.dependency_overrides[get_current_user] = mock_admin
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def analyst_client():
    app.dependency_overrides[get_current_user] = mock_analyst
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def no_auth_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
