"""Temporal helpers anchored on real data ranges instead of system date."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session


AnchorSource = Literal["analytics", "usage", "billing", "subscription", "churn"]

_ALLOWED_FIELDS: dict[str, set[str]] = {
    "user_activities": {"activity_datetime"},
    "billing_events": {"event_datetime"},
    "subscriptions": {"subscription_start_date", "subscription_end_date"},
    "unsubscriptions": {"unsubscription_datetime"},
}

_SOURCE_FIELDS: dict[AnchorSource, list[tuple[str, str]]] = {
    "usage": [
        ("user_activities", "activity_datetime"),
    ],
    "billing": [
        ("billing_events", "event_datetime"),
    ],
    "subscription": [
        ("subscriptions", "subscription_end_date"),
        ("subscriptions", "subscription_start_date"),
    ],
    "churn": [
        ("unsubscriptions", "unsubscription_datetime"),
        ("user_activities", "activity_datetime"),
        ("subscriptions", "subscription_end_date"),
        ("subscriptions", "subscription_start_date"),
    ],
    "analytics": [
        ("user_activities", "activity_datetime"),
        ("billing_events", "event_datetime"),
        ("unsubscriptions", "unsubscription_datetime"),
        ("subscriptions", "subscription_end_date"),
        ("subscriptions", "subscription_start_date"),
    ],
}


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _to_naive_utc(value: datetime | date | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, time.min)
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _is_allowed(table: str, field: str) -> bool:
    return field in _ALLOWED_FIELDS.get(table, set())


def _query_extreme(
    db: Session,
    *,
    table: str,
    field: str,
    aggregate: Literal["MIN", "MAX"],
    now_cap: datetime,
) -> datetime | None:
    if not _is_allowed(table, field):
        return None

    where = f" WHERE {field} IS NOT NULL"
    params: dict[str, object] = {}
    if aggregate == "MAX":
        where += f" AND {field} <= :now_cap"
        params["now_cap"] = now_cap

    try:
        result = db.execute(text(f"SELECT {aggregate}({field}) FROM {table}{where}"), params).scalar()
    except Exception:
        return None

    return _to_naive_utc(result)


def _source_points(db: Session, source: AnchorSource, aggregate: Literal["MIN", "MAX"]) -> list[datetime]:
    now_cap = _utc_now_naive()
    points: list[datetime] = []
    for table, field in _SOURCE_FIELDS[source]:
        value = _query_extreme(db, table=table, field=field, aggregate=aggregate, now_cap=now_cap)
        if value is not None:
            points.append(value)
    return points


def get_data_bounds(db: Session, source: AnchorSource = "analytics") -> tuple[datetime, datetime]:
    """Return clamped [min, max] bounds for a metric source."""
    mins = _source_points(db, source, "MIN")
    maxs = _source_points(db, source, "MAX")
    now_cap = _utc_now_naive()

    min_dt = min(mins) if mins else now_cap
    max_dt = min(max(maxs), now_cap) if maxs else now_cap

    if min_dt > max_dt:
        min_dt = max_dt
    return min_dt, max_dt


def get_data_anchor(
    db: Session,
    table: str = "billing_events",
    field: str = "event_datetime",
    *,
    source: AnchorSource | None = None,
) -> datetime:
    """Return a safe anchor date derived from real data and clamped to now."""
    if source is not None:
        _, anchor = get_data_bounds(db, source=source)
        return anchor

    now_cap = _utc_now_naive()
    value = _query_extreme(db, table=table, field=field, aggregate="MAX", now_cap=now_cap)
    if value is None:
        _, fallback_anchor = get_data_bounds(db, source="analytics")
        return fallback_anchor
    return min(value, now_cap)


def get_default_window(db: Session, days: int = 30, *, source: AnchorSource = "analytics") -> tuple[datetime, datetime]:
    data_start, anchor = get_data_bounds(db, source=source)
    start = anchor - timedelta(days=days)
    if start < data_start:
        start = data_start
    return start, anchor


def get_month_window(db: Session, *, source: AnchorSource = "analytics") -> tuple[datetime, datetime]:
    data_start, anchor = get_data_bounds(db, source=source)
    month_start = anchor.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if month_start < data_start:
        month_start = data_start
    return month_start, anchor


def get_week_window(db: Session, *, source: AnchorSource = "analytics") -> tuple[datetime, datetime]:
    data_start, anchor = get_data_bounds(db, source=source)
    start = anchor - timedelta(days=7)
    if start < data_start:
        start = data_start
    return start, anchor


def get_day_window(db: Session, *, source: AnchorSource = "analytics") -> tuple[datetime, datetime]:
    data_start, anchor = get_data_bounds(db, source=source)
    start = anchor - timedelta(hours=24)
    if start < data_start:
        start = data_start
    return start, anchor
