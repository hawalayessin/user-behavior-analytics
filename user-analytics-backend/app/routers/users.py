from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.database import get_db
from app.models import User, Subscription
from app.schemas.users import (
    UserListItem,
    UserListResponse,
    UserDetailResponse,
    SubscriptionItem,
    UnsubscriptionItem,
    UserStatsResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


# ───────────────── GET /users ─────────────────

@router.get("", response_model=None)
def list_users(
    status:     Optional[str]      = Query(None),
    date_from:  Optional[datetime] = Query(None),
    date_to:    Optional[datetime] = Query(None),
    search:     Optional[str]      = Query(None),
    service_id: Optional[str]      = Query(None),
    page:       int                = Query(1,  ge=1),
    page_size:  int                = Query(20, ge=1, le=200),
    db:         Session            = Depends(get_db),
):
    limit  = page_size
    offset = (page - 1) * page_size

    # ── Filtres dynamiques ────────────────────────────────────
    where_clauses = ["1=1"]
    params: dict  = {"limit": limit, "offset": offset}

    if status:
        where_clauses.append("u.status = :status")
        params["status"] = status

    if search:
        where_clauses.append("u.phone_number ILIKE :search")
        params["search"] = f"%{search}%"

    if date_from:
        where_clauses.append("u.created_at >= :date_from")
        params["date_from"] = date_from

    if date_to:
        where_clauses.append("u.created_at <= :date_to")
        params["date_to"] = date_to

    if service_id:
        where_clauses.append("""
            EXISTS (
                SELECT 1 FROM subscriptions sub
                WHERE sub.user_id    = u.id
                  AND sub.service_id = CAST(:service_id AS uuid)
                  AND sub.status IN ('active','trial')
            )
        """)
        params["service_id"] = service_id

    where_sql = " AND ".join(where_clauses)

    # ── Requête principale ────────────────────────────────────
    rows = db.execute(text(f"""
        SELECT
            u.id,
            u.phone_number,
            u.status,
            u.created_at,
            u.last_activity_at,
            EXTRACT(DAY FROM NOW() - u.last_activity_at)::int            AS days_inactive,
            COALESCE(
                ARRAY_AGG(DISTINCT srv.name)
                FILTER (WHERE s.status IN ('active','trial') AND srv.name IS NOT NULL),
                ARRAY[]::text[]
            )                                                             AS service_names,
            COALESCE(
                ARRAY_AGG(DISTINCT s.status)
                FILTER (WHERE s.status IN ('active','trial') AND s.status IS NOT NULL),
                ARRAY[]::text[]
            )                                                             AS service_statuses,
            COALESCE(
                ARRAY_AGG(DISTINCT s.service_id::text)
                FILTER (WHERE s.status IN ('active','trial') AND s.service_id IS NOT NULL),
                ARRAY[]::text[]
            )                                                             AS service_ids,
            COUNT(*) FILTER (WHERE s.id IS NOT NULL)                     AS total_subscriptions,
            COUNT(*) FILTER (WHERE s.status = 'active')                  AS active_subscriptions,
            EXISTS (
                SELECT 1 FROM unsubscriptions un
                JOIN subscriptions su ON su.id = un.subscription_id
                WHERE su.user_id = u.id
            )                                                             AS has_churned
        FROM users u
        LEFT JOIN subscriptions s   ON s.user_id  = u.id
        LEFT JOIN services srv      ON srv.id      = s.service_id
        WHERE {where_sql}
        GROUP BY u.id
        ORDER BY u.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params).fetchall()

    # ── Count total ───────────────────────────────────────────
    count_row = db.execute(text(f"""
        SELECT COUNT(DISTINCT u.id) AS total
        FROM users u
        LEFT JOIN subscriptions s ON s.user_id = u.id
        WHERE {where_sql}
    """), params).fetchone()

    # ── Sérialisation ─────────────────────────────────────────
    users_out = []
    for r in rows:
        names    = r.service_names    or []
        statuses = r.service_statuses or []
        ids      = r.service_ids      or []

        seen     = set()
        services = []
        for n, st, sid in zip(names, statuses, ids):
            if n not in seen:
                seen.add(n)
                services.append({"id": sid, "name": n, "status": st})

        users_out.append({
            "id":                   str(r.id),
            "phone_number":         r.phone_number,
            "status":               r.status,
            "created_at":           r.created_at.isoformat()       if r.created_at       else None,
            "last_activity_at":     r.last_activity_at.isoformat() if r.last_activity_at else None,
            "days_inactive":        r.days_inactive,
            "services":             services,
            "total_subscriptions":  r.total_subscriptions  or 0,
            "active_subscriptions": r.active_subscriptions or 0,
            "has_churned":          r.has_churned          or False,
        })

    return {
        "data":      users_out,
        "total":     count_row.total if count_row else 0,
        "page":      page,
        "page_size": page_size,
    }


# ───────────────── GET /users/stats/overview ─────────────────

@router.get("/stats/overview", response_model=UserStatsResponse)
def get_users_stats(db: Session = Depends(get_db)):
    now             = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    total_users       = db.query(func.count(User.id)).scalar() or 0
    active_users      = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
    inactive_users    = db.query(func.count(User.id)).filter(User.status == "inactive").scalar() or 0  # noqa: F841
    new_users_last_30 = db.query(func.count(User.id)).filter(User.created_at >= thirty_days_ago).scalar() or 0

    churned_users = (
        db.query(func.count(func.distinct(Subscription.user_id)))
        .filter(Subscription.status == "cancelled")
        .scalar() or 0
    )

    total_tried = (
        db.query(func.count(func.distinct(Subscription.user_id)))
        .filter(Subscription.status.in_(["active", "expired", "cancelled"]))
        .scalar() or 0
    )
    converted = (
        db.query(func.count(func.distinct(Subscription.user_id)))
        .filter(Subscription.status == "active")
        .scalar() or 0
    )
    conversion_rate = round((converted / total_tried) * 100, 2) if total_tried > 0 else 0.0

    return UserStatsResponse(
        total_users=total_users,
        active_users=active_users,
        churned_users=churned_users,
        new_users_last_30_days=new_users_last_30,
        conversion_rate=conversion_rate,
    )


# ───────────────── GET /users/{user_id} ─────────────────

@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(
            joinedload(User.subscriptions),
            joinedload(User.unsubscriptions),
        )
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