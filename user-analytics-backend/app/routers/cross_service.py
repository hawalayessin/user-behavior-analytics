"""
Cross-Service Behavior Analytics
4 endpoints analysing multi-service user behaviour.
All endpoints support optional filters: start_date, end_date, service_id.
"""

from datetime import date, timedelta
from typing import Optional
import logging
import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.date_ranges import resolve_date_range
from app.core.cache import build_cache_key, cache_or_compute, cached_endpoint
from app.core.config import settings


router = APIRouter(prefix="/analytics/cross-service", tags=["Cross-Service Behavior"])
logger = logging.getLogger(__name__)


def _cross_service_payload(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service_id: Optional[str] = None,
    **_: object,
) -> dict:
    return {
        "v": "cross-service-v3-arpu-status-fix",
        "start_date": start_date.isoformat() if start_date else "auto",
        "end_date": end_date.isoformat() if end_date else "auto",
        "service_id": service_id or "all",
    }


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _date_filter(alias: str = "sub") -> str:
    """Returns a SQL WHERE fragment for date range on subscription_start_date."""
    return (
        f" AND {alias}.subscription_start_date >= CAST(:start_dt AS timestamp)"
        f" AND {alias}.subscription_start_date <  CAST(:end_dt   AS timestamp) + INTERVAL '1 day'"
    )


def _service_filter(alias: str = "sub") -> str:
    return f" AND {alias}.service_id = CAST(:service_id AS uuid)"


def _build_where(has_date: bool, has_service: bool, alias: str = "sub") -> str:
    clauses = ""
    if has_date:
        clauses += _date_filter(alias)
    if has_service:
        clauses += _service_filter(alias)
    return clauses


def _resolve_params(
    db: Session,
    start_date: Optional[date],
    end_date: Optional[date],
    service_id: Optional[str],
) -> dict:
    """Resolve defaults and return a param dict."""
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")

    # Cross-service joins can get expensive on very large windows.
    # If the client sends no explicit range, clamp to a recent default window.
    if start_date is None and end_date is None:
        window_days = max(int(getattr(settings, "CROSS_SERVICE_DEFAULT_WINDOW_DAYS", 365)), 30)
        bounded_start = end_dt - timedelta(days=window_days - 1)
        if bounded_start > start_dt:
            start_dt = bounded_start

    return {
        "start_dt": start_dt,
        "end_dt": end_dt,
        "service_id": service_id,
    }


# ──────────────────────────────────────────────────────────────────────
# 1) GET /analytics/cross-service/overview
# ──────────────────────────────────────────────────────────────────────
@router.get("/overview")
@cached_endpoint(
    "cross_service_overview",
    settings.CROSS_SERVICE_CACHE_TTL_SECONDS,
    key_builder=_cross_service_payload,
)
def get_overview(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    """
    Multi-service users, top combo, cross-retention vs mono-retention, ARPU.
    """
    params = _resolve_params(db, start_date, end_date, service_id)
    has_date = True
    has_service = bool(service_id)
    wh = _build_where(has_date, has_service, "sub")

    # --- multi-service users ---
    multi = db.execute(
        text(f"""
            WITH filtered_subs AS (
                SELECT sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1 {wh}
            ),
            user_service_count AS (
                SELECT user_id, COUNT(DISTINCT service_id) AS nb_services
                FROM filtered_subs
                GROUP BY user_id
            )
            SELECT
                COUNT(*) FILTER (WHERE nb_services >= 2) AS multi_users,
                COUNT(*)                                 AS total_users
            FROM user_service_count
        """),
        params,
    ).fetchone()

    multi_users = int(multi.multi_users or 0)
    total_users = int(multi.total_users or 0)
    multi_rate = round(multi_users * 100.0 / total_users, 1) if total_users > 0 else 0

    # --- top combo (pair of services) ---
    combo = db.execute(
        text(f"""
            WITH filtered_subs AS (
                SELECT DISTINCT sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1 {wh}
            )
            SELECT s1.name AS service_a, s2.name AS service_b, COUNT(*) AS combo_count
            FROM filtered_subs fs1
            JOIN filtered_subs fs2
              ON fs1.user_id = fs2.user_id
              AND fs1.service_id < fs2.service_id
            JOIN services s1 ON fs1.service_id = s1.id
            JOIN services s2 ON fs2.service_id = s2.id
            GROUP BY s1.name, s2.name
            ORDER BY combo_count DESC
            LIMIT 1
        """),
        params,
    ).fetchone()

    top_combo = {
        "service_a": combo.service_a if combo else "—",
        "service_b": combo.service_b if combo else "—",
        "count": int(combo.combo_count) if combo else 0,
    }

    # --- cross-retention (D30) vs mono-retention ---
    retention = db.execute(
        text(f"""
            WITH filtered_subs AS (
                SELECT sub.user_id, sub.service_id, sub.subscription_start_date, sub.subscription_end_date
                FROM subscriptions sub
                WHERE 1=1 {wh}
            ),
            user_service_count AS (
                SELECT user_id, COUNT(DISTINCT service_id) AS nb_services
                FROM filtered_subs
                GROUP BY user_id
            ),
            sub_with_seg AS (
                SELECT
                    fs.user_id,
                    fs.subscription_start_date,
                    fs.subscription_end_date,
                    CASE WHEN usc.nb_services >= 2 THEN 'multi' ELSE 'mono' END AS segment
                FROM filtered_subs fs
                JOIN user_service_count usc ON usc.user_id = fs.user_id
            )
            SELECT
                segment,
                COUNT(*) AS total,
                COUNT(*) FILTER (
                    WHERE subscription_end_date IS NULL
                       OR EXTRACT(DAY FROM subscription_end_date - subscription_start_date) >= 30
                ) AS retained_d30
            FROM sub_with_seg
            GROUP BY segment
        """),
        params,
    ).fetchall()

    cross_retention = 0.0
    mono_retention = 0.0
    for row in retention:
        rate = round(int(row.retained_d30) * 100.0 / int(row.total), 1) if int(row.total) > 0 else 0
        if row.segment == "multi":
            cross_retention = rate
        else:
            mono_retention = rate

    # --- ARPU multi vs mono ---
    arpu = db.execute(
        text(f"""
            WITH filtered_subs AS (
                SELECT sub.id, sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1 {wh}
            ),
            user_service_count AS (
                SELECT user_id, COUNT(DISTINCT service_id) AS nb_services
                FROM filtered_subs
                GROUP BY user_id
            ),
            user_revenue AS (
                SELECT
                    fs.user_id,
                    CASE WHEN usc.nb_services >= 2 THEN 'multi' ELSE 'mono' END AS segment,
                    COALESCE(
                        SUM(st.price) FILTER (
                            WHERE UPPER(TRIM(COALESCE(be.status, ''))) = 'SUCCESS'
                        ),
                        0
                    ) AS revenue
                FROM filtered_subs fs
                JOIN user_service_count usc ON usc.user_id = fs.user_id
                LEFT JOIN billing_events be ON be.subscription_id = fs.id
                LEFT JOIN services sv ON sv.id = fs.service_id
                LEFT JOIN service_types st ON st.id = sv.service_type_id
                GROUP BY fs.user_id, segment
            )
            SELECT
                segment,
                COUNT(DISTINCT user_id) AS user_count,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM user_revenue
            GROUP BY segment
        """),
        params,
    ).fetchall()

    arpu_multi = 0.0
    arpu_mono = 0.0
    for row in arpu:
        count = int(row.user_count or 0)
        rev = float(row.total_revenue or 0)
        avg = round(rev / count, 2) if count > 0 else 0.0
        if row.segment == "multi":
            arpu_multi = avg
        else:
            arpu_mono = avg

    return {
        "multi_service_users": multi_users,
        "multi_service_rate": multi_rate,
        "top_combo": top_combo,
        "cross_retention_rate": cross_retention,
        "mono_retention_rate": mono_retention,
        "arpu_multi": arpu_multi,
        "arpu_mono": arpu_mono,
    }


# ──────────────────────────────────────────────────────────────────────
# 2) GET /analytics/cross-service/co-subscriptions
# ──────────────────────────────────────────────────────────────────────
@router.get("/co-subscriptions")
@cached_endpoint(
    "cross_service_co_subscriptions",
    settings.CROSS_SERVICE_CACHE_TTL_SECONDS,
    key_builder=_cross_service_payload,
)
def get_co_subscriptions(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    """
    Co-subscription matrix: for each pair (A, B) what % of A users also have B.
    Returns both directions for a full heatmap matrix.
    """
    params = _resolve_params(db, start_date, end_date, service_id)
    has_date = True
    has_service = bool(service_id)
    wh = _build_where(has_date, has_service, "sub")

    rows = db.execute(
        text(f"""
            WITH filtered_subs AS (
                SELECT DISTINCT sub.user_id, sub.service_id
                FROM subscriptions sub
                WHERE 1=1 {wh}
            ),
            service_user_counts AS (
                SELECT service_id, COUNT(DISTINCT user_id) AS total_users
                FROM filtered_subs
                GROUP BY service_id
            ),
            pairs AS (
                SELECT
                    us1.service_id AS sid_a,
                    us2.service_id AS sid_b,
                    COUNT(DISTINCT us1.user_id) AS co_count
                FROM filtered_subs us1
                JOIN filtered_subs us2
                  ON us1.user_id = us2.user_id
                  AND us1.service_id <> us2.service_id
                GROUP BY us1.service_id, us2.service_id
            )
            SELECT
                s1.name AS service_a,
                s2.name AS service_b,
                p.co_count,
                ROUND(p.co_count * 100.0 / NULLIF(suc.total_users, 0), 1) AS rate
            FROM pairs p
            JOIN services s1 ON p.sid_a = s1.id
            JOIN services s2 ON p.sid_b = s2.id
            JOIN service_user_counts suc ON suc.service_id = p.sid_a
            ORDER BY p.co_count DESC
        """),
        params,
    ).fetchall()

    return {
        "matrix": [
            {
                "service_a": r.service_a,
                "service_b": r.service_b,
                "co_count": int(r.co_count or 0),
                "rate": float(r.rate or 0),
            }
            for r in rows
        ]
    }


# ──────────────────────────────────────────────────────────────────────
# 3) GET /analytics/cross-service/migrations
# ──────────────────────────────────────────────────────────────────────
@router.get("/migrations")
@cached_endpoint(
    "cross_service_migrations",
    settings.CROSS_SERVICE_CACHE_TTL_SECONDS,
    key_builder=_cross_service_payload,
)
def get_migrations(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    """
    Top migration flows: user subscribed to service A, ended, then subscribed to service B.
    """
    params = _resolve_params(db, start_date, end_date, service_id)
    has_date = True
    has_service = bool(service_id)
    wh1 = _build_where(has_date, has_service, "sub1")
    wh2 = _build_where(has_date, has_service, "sub2")

    total_users_row = db.execute(
        text(f"""
            SELECT COUNT(DISTINCT sub.user_id) AS cnt
            FROM subscriptions sub
            WHERE 1=1 {_build_where(has_date, has_service, "sub")}
        """),
        params,
    ).fetchone()
    total_users = int(total_users_row.cnt or 0) if total_users_row else 1

    rows = db.execute(
        text(f"""
            SELECT
                s1.name AS from_service,
                s2.name AS to_service,
                COUNT(DISTINCT sub1.user_id) AS user_count
            FROM subscriptions sub1
            JOIN subscriptions sub2
              ON sub1.user_id = sub2.user_id
              AND sub2.subscription_start_date > sub1.subscription_start_date
              AND sub1.service_id <> sub2.service_id
            JOIN services s1 ON sub1.service_id = s1.id
            JOIN services s2 ON sub2.service_id = s2.id
            WHERE sub1.subscription_end_date IS NOT NULL
              AND sub2.subscription_start_date > sub1.subscription_end_date
              {wh1.replace(" AND sub1.", " AND sub1.")}
            GROUP BY s1.name, s2.name
            ORDER BY user_count DESC
            LIMIT 10
        """),
        params,
    ).fetchall()

    migration_items = [
        {
            "from_service": r.from_service,
            "to_service": r.to_service,
            "user_count": int(r.user_count or 0),
            "migration_rate": round(
                int(r.user_count or 0) * 100.0 / total_users, 2
            ) if total_users > 0 else 0,
        }
        for r in rows
    ]

    top_paths = migration_items[:5]
    top3_users = sum(int(x.get("user_count") or 0) for x in migration_items[:3])
    total_migration_users = sum(int(x.get("user_count") or 0) for x in migration_items)
    concentration_top3 = round((top3_users * 100.0 / total_migration_users), 1) if total_migration_users > 0 else 0.0

    standardized_paths = []
    for idx, m in enumerate(top_paths, start=1):
        rate = float(m.get("migration_rate") or 0)
        users = int(m.get("user_count") or 0)

        if rate >= 5 or users >= 10000:
            priority = "high"
            business_signal = "strong_substitution"
            action = "Launch targeted cross-sell within 72h after churn risk is detected on source service."
        elif rate >= 2 or users >= 3000:
            priority = "medium"
            business_signal = "emerging_path"
            action = "Create a bundled offer and in-app recommendation flow between source and destination services."
        else:
            priority = "low"
            business_signal = "long_tail_path"
            action = "Keep path in monitoring and test low-cost messaging campaigns before scaling."

        standardized_paths.append(
            {
                "rank": idx,
                "path_code": f"{m['from_service']}->{m['to_service']}",
                "from_service": m["from_service"],
                "to_service": m["to_service"],
                "user_count": users,
                "migration_rate": rate,
                "priority": priority,
                "business_signal": business_signal,
                "recommended_action": action,
            }
        )

    management_notes = [
        f"Top 3 paths represent {concentration_top3}% of observed migration flows.",
        "Use high-priority paths for immediate retention playbooks and medium-priority paths for bundle experiments.",
        "Track conversion lift from each standardized A->B playbook monthly to validate business impact.",
    ]

    return {
        "migrations": migration_items,
        "standardized_paths": standardized_paths,
        "summary": {
            "total_users_in_scope": total_users,
            "total_migration_users": total_migration_users,
            "top3_concentration_pct": concentration_top3,
        },
        "management_notes": management_notes,
    }


# ──────────────────────────────────────────────────────────────────────
# 4) GET /analytics/cross-service/distribution
# ──────────────────────────────────────────────────────────────────────
@router.get("/distribution")
@cached_endpoint(
    "cross_service_distribution",
    settings.CROSS_SERVICE_CACHE_TTL_SECONDS,
    key_builder=_cross_service_payload,
)
def get_distribution(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    """
    How many services does a typical user subscribe to?
    """
    params = _resolve_params(db, start_date, end_date, service_id)
    has_date = True
    has_service = bool(service_id)
    wh = _build_where(has_date, has_service, "sub")

    rows = db.execute(
        text(f"""
            SELECT
                nb_services,
                COUNT(*) AS user_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
            FROM (
                SELECT sub.user_id, COUNT(DISTINCT sub.service_id) AS nb_services
                FROM subscriptions sub
                WHERE 1=1 {wh}
                GROUP BY sub.user_id
            ) t
            GROUP BY nb_services
            ORDER BY nb_services
        """),
        params,
    ).fetchall()

    return {
        "distribution": [
            {
                "nb_services": int(r.nb_services),
                "user_count": int(r.user_count),
                "percentage": float(r.percentage or 0),
            }
            for r in rows
        ]
    }


@router.get("/all")
def get_all_cross_service(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")
    cache_key = build_cache_key(
        "cross-service:all",
        {
            "v": "cross-service-v3-arpu-status-fix",
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "service_id": service_id or "all",
        },
    )

    def _safe_compute(section_name: str, compute_fn, fallback):
        t0 = time.perf_counter()
        try:
            value = compute_fn()
            took_ms = round((time.perf_counter() - t0) * 1000)
            logger.info("cross_service.%s computed in %sms", section_name, took_ms)
            return value, None, took_ms
        except OperationalError as exc:
            took_ms = round((time.perf_counter() - t0) * 1000)
            logger.warning("cross_service.%s failed after %sms: %s", section_name, took_ms, exc)
            return fallback, "database_timeout", took_ms
        except Exception as exc:  # keep endpoint resilient for dashboard rendering
            took_ms = round((time.perf_counter() - t0) * 1000)
            logger.exception("cross_service.%s unexpected failure after %sms", section_name, took_ms)
            return fallback, "internal_error", took_ms

    def _compute_all_payload():
        overview, overview_error, overview_ms = _safe_compute(
            "overview",
            lambda: get_overview(
                db=db,
                start_date=start_dt,
                end_date=end_dt,
                service_id=service_id,
            ),
            {
                "multi_service_users": 0,
                "multi_service_rate": 0,
                "top_combo": {"service_a": "-", "service_b": "-", "count": 0},
                "cross_retention_rate": 0,
                "mono_retention_rate": 0,
                "arpu_multi": 0,
                "arpu_mono": 0,
            },
        )

        co_subscriptions, co_subscriptions_error, co_subscriptions_ms = _safe_compute(
            "co_subscriptions",
            lambda: get_co_subscriptions(
                db=db,
                start_date=start_dt,
                end_date=end_dt,
                service_id=service_id,
            ),
            {"matrix": []},
        )

        migrations, migrations_error, migrations_ms = _safe_compute(
            "migrations",
            lambda: get_migrations(
                db=db,
                start_date=start_dt,
                end_date=end_dt,
                service_id=service_id,
            ),
            {
                "migrations": [],
                "standardized_paths": [],
                "summary": {
                    "total_users_in_scope": 0,
                    "total_migration_users": 0,
                    "top3_concentration_pct": 0,
                },
                "management_notes": [],
            },
        )

        distribution, distribution_error, distribution_ms = _safe_compute(
            "distribution",
            lambda: get_distribution(
                db=db,
                start_date=start_dt,
                end_date=end_dt,
                service_id=service_id,
            ),
            {"distribution": []},
        )

        return {
            "overview": overview,
            "co_subscriptions": co_subscriptions,
            "migrations": migrations,
            "distribution": distribution,
            "meta": {
                "window": {
                    "start_date": start_dt.isoformat(),
                    "end_date": end_dt.isoformat(),
                },
                "timings_ms": {
                    "overview": overview_ms,
                    "co_subscriptions": co_subscriptions_ms,
                    "migrations": migrations_ms,
                    "distribution": distribution_ms,
                },
                "errors": {
                    "overview": overview_error,
                    "co_subscriptions": co_subscriptions_error,
                    "migrations": migrations_error,
                    "distribution": distribution_error,
                },
            },
        }

    return cache_or_compute(
        cache_key,
        settings.CROSS_SERVICE_CACHE_TTL_SECONDS,
        compute_function=_compute_all_payload,
    )
