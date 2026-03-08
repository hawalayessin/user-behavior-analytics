from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
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

@router.get("", response_model=UserListResponse)
def list_users(
    status: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):

    query = db.query(User).options(
        joinedload(User.subscriptions),
        joinedload(User.unsubscriptions),
    )

    if status:
        query = query.filter(User.status == status)
    if date_from:
        query = query.filter(User.created_at >= date_from)
    if date_to:
        query = query.filter(User.created_at <= date_to)

    total = db.query(func.count(User.id))
    if status:
        total = total.filter(User.status == status)
    if date_from:
        total = total.filter(User.created_at >= date_from)
    if date_to:
        total = total.filter(User.created_at <= date_to)

    total = total.scalar() or 0

    users = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []

    for user in users:
        total_subs = len(user.subscriptions)
        active_subs = sum(1 for s in user.subscriptions if s.status == "active")

        items.append(
            UserListItem(
                id=user.id,
                phone=user.phone_number,
                status=user.status,
                created_at=user.created_at,
                last_active_at=user.last_activity_at,
                total_subscriptions=total_subs,
                active_subscriptions=active_subs,
                has_churned=len(user.unsubscriptions) > 0,
            )
        )

    return UserListResponse(
        data=items,
        total=total,
        page=page,
        page_size=page_size,
    )


# ───────────────── STATS ─────────────────

@router.get("/stats/overview", response_model=UserStatsResponse)
def get_users_stats(db: Session = Depends(get_db)):
    now             = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    total_users       = db.query(func.count(User.id)).scalar() or 0
    active_users      = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
    inactive_users    = db.query(func.count(User.id)).filter(User.status == "inactive").scalar() or 0
    new_users_last_30 = db.query(func.count(User.id)).filter(User.created_at >= thirty_days_ago).scalar() or 0

    # ✅ Churn calculé depuis subscriptions (pas depuis users.status)
    churned_users = (
        db.query(func.count(func.distinct(Subscription.user_id)))
        .filter(Subscription.status == "cancelled")
        .scalar() or 0
    )

    # ✅ Conversion sans converted_from_trial
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



# ───────────────── GET /users/{id} ─────────────────

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