from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models import User
from app.schemas.users import UserDetailResponse

router = APIRouter(prefix="/users", tags=["Users"])


def _exec_with_timeout_retry(db: Session, sql_text, params: dict):
    try:
        return db.execute(sql_text, params)
    except OperationalError as exc:
        if "statement timeout" not in str(exc).lower():
            raise
        db.rollback()
        db.execute(text("SET LOCAL statement_timeout = 0"))
        return db.execute(sql_text, params)


# ─────────────────────────────────────────────
# ✅ GET /users  (LIST USERS + CAMPAIGN)
# ─────────────────────────────────────────────

@router.get("", response_model=None)
def list_users(
    status:     Optional[str]      = Query(None),
    date_from:  Optional[datetime] = Query(None),
    date_to:    Optional[datetime] = Query(None),
    search:     Optional[str]      = Query(None),
    service_id: Optional[str]      = Query(None),
    page:       int                = Query(1, ge=1),
    page_size:  int                = Query(10, ge=1, le=200),
    cursor_created_at: Optional[datetime] = Query(None),
    cursor_id: Optional[str] = Query(None),
    export:     bool               = Query(False),   # ✅ NOUVEAU
    db:         Session            = Depends(get_db),
):
    # ── Si export=true → pas de limite ───────
    if export:
        limit  = None
    else:
        limit  = page_size

    # ── filtres dynamiques ────────────────────
    where_clauses = ["1=1"]
    paging_where_clauses = ["1=1"]
    params: dict  = {}

    if not export:
        params["limit"]  = limit

    if status:
        where_clauses.append("u.status = :status")
        paging_where_clauses.append("u.status = :status")
        params["status"] = status

    if search:
        where_clauses.append("u.phone_number ILIKE :search")
        paging_where_clauses.append("u.phone_number ILIKE :search")
        params["search"] = f"%{search}%"

    if date_from:
        where_clauses.append("u.created_at >= :date_from")
        paging_where_clauses.append("u.created_at >= :date_from")
        params["date_from"] = date_from

    if date_to:
        where_clauses.append("u.created_at <= :date_to")
        paging_where_clauses.append("u.created_at <= :date_to")
        params["date_to"] = date_to

    if service_id:
        where_clauses.append("""
            EXISTS (
                SELECT 1
                FROM subscriptions sub
                WHERE sub.user_id = u.id
                  AND sub.service_id = CAST(:service_id AS uuid)
            )
        """)
        paging_where_clauses.append("""
            EXISTS (
                SELECT 1
                FROM subscriptions sub
                WHERE sub.user_id = u.id
                  AND sub.service_id = CAST(:service_id AS uuid)
            )
        """)
        params["service_id"] = service_id

    if not export and cursor_created_at and cursor_id:
        paging_where_clauses.append("(u.created_at, u.id) < (:cursor_created_at, CAST(:cursor_id AS uuid))")
        params["cursor_created_at"] = cursor_created_at
        params["cursor_id"] = cursor_id

    where_sql = " AND ".join(where_clauses)
    paging_where_sql = " AND ".join(paging_where_clauses)
    sf_unsub = "AND un.service_id = CAST(:service_id AS uuid)" if service_id else ""

    # ── requête principale optimisée ──────────
    # 1) Paginer d'abord la table users
    # 2) Agréger subscriptions/services seulement pour les users de la page
    limit_clause = "" if export else "LIMIT :limit"
    paging_where_for_query = where_sql if export else paging_where_sql

    users_query = text(f"""
        WITH paged_users AS (
            SELECT
                u.id,
                u.phone_number,
                u.status,
                u.created_at
            FROM users u
            WHERE {paging_where_for_query}
            ORDER BY u.created_at DESC, u.id DESC
            {limit_clause}
        )
        SELECT
            pu.id,
            pu.phone_number,
            pu.status,
            pu.created_at,
            lu.last_activity_at,
            COALESCE(ss.services, '[]'::jsonb) AS services,
            COALESCE(ss.total_subscriptions, 0) AS total_subscriptions,
            COALESCE(ss.active_subscriptions, 0) AS active_subscriptions,
            camp.campaign_name
        FROM paged_users pu
        LEFT JOIN LATERAL (
            SELECT MAX(un.unsubscription_datetime) AS last_activity_at
            FROM unsubscriptions un
            WHERE un.user_id = pu.id
            {sf_unsub}
        ) lu ON TRUE
        LEFT JOIN LATERAL (
            SELECT
                COALESCE(
                    jsonb_agg(DISTINCT jsonb_build_object('id', s.service_id::text, 'name', srv.name))
                    FILTER (WHERE s.service_id IS NOT NULL),
                    '[]'::jsonb
                ) AS services,
                COUNT(*) FILTER (WHERE s.id IS NOT NULL) AS total_subscriptions,
                COUNT(*) FILTER (WHERE s.status = 'active') AS active_subscriptions
            FROM subscriptions s
            LEFT JOIN services srv ON srv.id = s.service_id
            WHERE s.user_id = pu.id
        ) ss ON TRUE
        LEFT JOIN LATERAL (
            SELECT c.name AS campaign_name
            FROM subscriptions sub
            JOIN campaigns c ON c.id = sub.campaign_id
            WHERE sub.user_id = pu.id
              AND c.status = 'sent'
            ORDER BY c.send_datetime DESC
            LIMIT 1
        ) camp ON TRUE
        ORDER BY pu.created_at DESC, pu.id DESC
    """)
    rows = _exec_with_timeout_retry(db, users_query, params).fetchall()

    # ── count total ───────────────────────────
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_query = text(f"""
        SELECT COUNT(*) AS total
        FROM users u
        WHERE {where_sql}
    """)
    count_row = _exec_with_timeout_retry(db, count_query, count_params).fetchone()

    # ── serialization ─────────────────────────
    users_out = []
    for r in rows:
        users_out.append({
            "id":                   str(r.id),
            "phone_number":         r.phone_number,
            "status":               r.status,
            "created_at":           r.created_at.isoformat() if r.created_at else None,
            "last_activity_at":     r.last_activity_at.isoformat() if r.last_activity_at else None,
            "services":             r.services or [],
            "total_subscriptions":  r.total_subscriptions or 0,
            "active_subscriptions": r.active_subscriptions or 0,
            "campaign_name":        r.campaign_name,
        })

    next_cursor = None
    if not export and rows:
        last_row = rows[-1]
        if last_row.created_at and last_row.id:
            next_cursor = {
                "created_at": last_row.created_at.isoformat(),
                "id": str(last_row.id),
            }

    return {
        "data":      users_out,
        "total":     count_row.total if count_row else 0,
        "page":      page,
        "page_size": page_size,
        "next_cursor": next_cursor,
    }


# ─────────────────────────────────────────────
# ✅ GET /users/trial  (LIST TRIAL USERS)
# ─────────────────────────────────────────────

@router.get("/trial", response_model=None)
def list_trial_users(
    status:     Optional[str]      = Query(None),
    search:     Optional[str]      = Query(None),
    service_id: Optional[str]      = Query(None),
    page:       int                = Query(1, ge=1),
    page_size:  int                = Query(20, ge=1, le=200),
    export:     bool               = Query(False),
    db:         Session            = Depends(get_db),
):
    """
    Get trial users with their trial details
    Status filter: 'active', 'converted', 'dropped'
    """
    # ── Si export=true → pas de limite ───────
    if export:
        limit  = 10000  # Max limit for export
        offset = 0
    else:
        limit  = page_size
        offset = (page - 1) * page_size

    # ── filtres dynamiques ────────────────────
    where_clauses = ["1=1"]
    params: dict  = {
        "limit":  limit,
        "offset": offset,
    }

    # Map frontend status to subscription status
    status_map = {
        "active":    "trial",
        "converted": "active",
        "dropped":   ["cancelled", "expired"],
    }

    if status and status in status_map:
        mapped_status = status_map[status]
        if isinstance(mapped_status, list):
            placeholders = ", ".join([f":status_{i}" for i in range(len(mapped_status))])
            where_clauses.append(f"sub.status IN ({placeholders})")
            for i, st in enumerate(mapped_status):
                params[f"status_{i}"] = st
        else:
            where_clauses.append("sub.status = :status")
            params["status"] = mapped_status

    if search:
        where_clauses.append("u.phone_number ILIKE :search")
        params["search"] = f"%{search}%"

    if service_id:
        where_clauses.append("sub.service_id = CAST(:service_id AS uuid)")
        params["service_id"] = service_id

    where_sql = " AND ".join(where_clauses)

    # ── requête principale ────────────────────
    limit_clause = "" if export else "LIMIT :limit OFFSET :offset"

    rows = db.execute(text(f"""
        SELECT
            u.id,
            u.phone_number,
            sub.id AS subscription_id,
            srv.name AS service_name,
            sub.subscription_start_date AS trial_start_date,
            sub.subscription_end_date AS trial_end_date,
            sub.status,
            EXTRACT(DAY FROM COALESCE(sub.subscription_end_date, NOW()) - sub.subscription_start_date)::integer AS trial_duration_days,
            CASE
                WHEN sub.status = 'trial' THEN 'active'
                WHEN sub.status = 'active' THEN 'converted'
                WHEN sub.status IN ('cancelled', 'expired') THEN 'dropped'
                ELSE 'unknown'
            END AS display_status

        FROM subscriptions sub
        JOIN users u ON u.id = sub.user_id
        JOIN services srv ON srv.id = sub.service_id

        WHERE {where_sql}

        ORDER BY sub.subscription_start_date DESC
        {limit_clause}
    """), params).fetchall()

    # ── count total ───────────────────────────
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}
    count_row = db.execute(text(f"""
        SELECT COUNT(DISTINCT sub.id) AS total
        FROM subscriptions sub
        JOIN users u ON u.id = sub.user_id
        JOIN services srv ON srv.id = sub.service_id
        WHERE {where_sql}
    """), count_params).fetchone()

    # ── serialization ─────────────────────────
    trial_users_out = []
    for r in rows:
        trial_users_out.append({
            "id":                   str(r.id),
            "phone_number":         r.phone_number,
            "service_name":         r.service_name,
            "trial_start_date":     r.trial_start_date.isoformat() if r.trial_start_date else None,
            "trial_end_date":       r.trial_end_date.isoformat() if r.trial_end_date else None,
            "status":               r.display_status,
            "trial_duration_days":  r.trial_duration_days or 0,
        })

    return {
        "data":      trial_users_out,
        "total":     count_row.total if count_row else 0,
        "page":      page,
        "page_size": page_size,
    }


# ─────────────────────────────────────────────
# ✅ GET /users/{id}
# ─────────────────────────────────────────────

@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(joinedload(User.subscriptions), joinedload(User.unsubscriptions))
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserDetailResponse(
        id=user.id,
        phone=user.phone_number,
        status=user.status,
        created_at=user.created_at,
        last_active_at=user.last_activity_at,
        subscriptions=user.subscriptions,
        unsubscriptions=user.unsubscriptions,
    )
