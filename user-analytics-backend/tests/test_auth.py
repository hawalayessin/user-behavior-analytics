from __future__ import annotations

from types import SimpleNamespace
import uuid

import pytest

from app.core.database import get_db
from app.main import app
from app.routers import auth as auth_router


class _FakeQuery:
    def __init__(self, user):
        self._user = user

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._user


class _FakeDB:
    def __init__(self, user):
        self._user = user

    def query(self, _model):
        return _FakeQuery(self._user)

    def commit(self):
        return None


@pytest.mark.anyio
async def test_login_valid(no_auth_client, monkeypatch):
    """Verify that valid credentials return a bearer JWT payload."""
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash="hashed",
        role="admin",
        full_name="Admin User",
        is_active=True,
    )

    def _override_get_db():
        yield _FakeDB(user)

    app.dependency_overrides[get_db] = _override_get_db
    monkeypatch.setattr(auth_router, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(auth_router, "create_access_token", lambda data, expires_delta: "jwt_test_token")

    response = await no_auth_client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "correct_password"},
    )

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid(no_auth_client, monkeypatch):
    """Verify that invalid password returns HTTP 401."""
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash="hashed",
        role="admin",
        full_name="Admin User",
        is_active=True,
    )

    def _override_get_db():
        yield _FakeDB(user)

    app.dependency_overrides[get_db] = _override_get_db
    monkeypatch.setattr(auth_router, "verify_password", lambda plain, hashed: False)

    response = await no_auth_client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "wrong"},
    )

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 401
