"""Initialize an empty disposable PostgreSQL schema, never an existing database.

The inherited Alembic history starts with an empty baseline and cannot recreate
the historical database from scratch. This explicit demo bootstrap does not stamp
or rewrite that migration history and must not be used on an existing deployment.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def require_disposable_database(url: str, confirmed: bool) -> None:
    from sqlalchemy.engine import make_url

    parsed = make_url(url)
    if not confirmed or not (parsed.database or "").endswith(("_demo", "_test")):
        raise ValueError("Requires --confirm-empty-demo and a database ending in _demo or _test.")
    if not parsed.drivername.startswith("postgresql"):
        raise ValueError("This bootstrap supports disposable PostgreSQL databases only.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-empty-demo", action="store_true")
    parser.add_argument("--users", type=int, default=0, help="Optional synthetic users, from 0 to 1000.")
    args = parser.parse_args()
    from app.core.config import settings

    require_disposable_database(settings.DATABASE_URL, args.confirm_empty_demo)
    if not 0 <= args.users <= 1000:
        parser.error("--users must be between 0 and 1000")

    from sqlalchemy import inspect
    from app.core.database import Base, engine, SessionLocal
    from app.models import User, ServiceType, Service, Subscription, UserActivity

    # An exclusive advisory lock prevents two bootstrap invocations from racing.
    with engine.begin() as connection:
        from sqlalchemy import text

        connection.execute(text("SELECT pg_advisory_xact_lock(67102218)"))
        if inspect(connection).get_table_names():
            raise RuntimeError("Database is not empty. No schema was changed.")
        Base.metadata.create_all(connection)

    if args.users:
        anchor = datetime(2025, 10, 31, tzinfo=timezone.utc)
        with SessionLocal.begin() as session:
            kind = ServiceType(id=uuid.uuid4(), name="demo_daily", billing_frequency_days=1,
                               price=Decimal("1.00"), trial_duration_days=3)
            session.add(kind)
            session.flush()
            service = Service(id=uuid.uuid4(), name="Synthetic demo service", service_type_id=kind.id)
            session.add(service)
            session.flush()
            for index in range(args.users):
                user = User(id=uuid.uuid4(), phone_number=f"demo-user-{index:04d}",
                            status="active", created_at=anchor-timedelta(days=30), last_activity_at=anchor)
                session.add(user)
                session.flush()
                session.add(Subscription(id=uuid.uuid4(), user_id=user.id, service_id=service.id,
                    subscription_start_date=anchor-timedelta(days=10+index%20), status="trial" if index%4==0 else "active"))
                session.add(UserActivity(id=uuid.uuid4(), user_id=user.id, service_id=service.id,
                    activity_datetime=anchor-timedelta(days=index%7), activity_type="service_usage"))
    print(f"Disposable ORM schema initialized with {args.users} synthetic users. Alembic history was not stamped.")


if __name__ == "__main__":
    main()
