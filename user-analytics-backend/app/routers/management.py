from __future__ import annotations

import re
import uuid
from datetime import date, datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.repositories.campaign_repo import CampaignRepository


router = APIRouter(prefix="/admin/management", tags=["Admin Management"])


BillingType = Literal["daily", "weekly"]
PHONE_REGEX = re.compile(r"^\+?[0-9]{8,15}$")


def _slug(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "service"


def _billing_to_days(billing_type: BillingType) -> int:
    return 1 if billing_type == "daily" else 7


def _service_type_name(service_name: str, billing_type: BillingType) -> str:
    # service_types.name is unique in this DB. Use a per-service unique name.
    return f"{_slug(service_name)}-{billing_type}"


def _campaign_status(send_dt: datetime) -> str:
    today = date.today()
    d = send_dt.date()
    if d < today:
        return "completed"
    if d > today:
        return "scheduled"
    return "active"


class ServiceCreateBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    billing_type: BillingType
    price: float = Field(..., gt=0)


class ServiceUpdateBody(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    billing_type: Optional[BillingType] = None
    price: Optional[float] = Field(default=None, gt=0)


class CampaignCreateBody(BaseModel):
    class TargetRow(BaseModel):
        phone_number: str = Field(..., min_length=1, max_length=20)
        segment: Optional[str] = Field(default=None, max_length=100)
        region: Optional[str] = Field(default=None, max_length=100)

    name: str = Field(..., min_length=1, max_length=255)
    service_id: uuid.UUID
    send_date: datetime
    target_size: int = Field(..., gt=0)
    targets: Optional[list[TargetRow]] = None


def _sanitize_targets(rows: Optional[list[CampaignCreateBody.TargetRow]]) -> list[dict]:
    if not rows:
        return []

    valid: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        phone = str(row.phone_number or "").strip().strip("'\"")
        if not phone:
            continue
        if not PHONE_REGEX.match(phone):
            continue
        if phone in seen:
            continue
        seen.add(phone)
        valid.append(
            {
                "phone_number": phone,
                "segment": (str(row.segment).strip() if row.segment else None),
                "region": (str(row.region).strip() if row.region else None),
            }
        )
    return valid


class CampaignUpdateBody(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    send_date: Optional[datetime] = None
    target_size: Optional[int] = Field(default=None, gt=0)


@router.get("/services")
def list_services(
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    rows = db.execute(
        text(
            """
            SELECT
              sv.id,
              sv.name,
              st.name AS service_type_name,
              st.billing_frequency_days,
              st.price,
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = sv.id) AS total_subscriptions,
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = sv.id AND s.status = 'active') AS active_subscriptions,
              (SELECT COUNT(*) FROM campaigns c WHERE c.service_id = sv.id) AS total_campaigns,
              sv.created_at
            FROM services sv
            JOIN service_types st ON st.id = sv.service_type_id
            WHERE sv.is_active = true
            ORDER BY sv.name ASC
            """
        )
    ).fetchall()

    def _billing_type(days: int) -> str:
        return "daily" if int(days or 0) == 1 else "weekly" if int(days or 0) == 7 else "daily"

    return [
        {
            "id": str(r.id),
            "name": r.name,
            "billing_type": _billing_type(r.billing_frequency_days),
            "price": float(r.price or 0),
            "total_subscriptions": int(r.total_subscriptions or 0),
            "active_subscriptions": int(r.active_subscriptions or 0),
            "total_campaigns": int(r.total_campaigns or 0),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/services", status_code=status.HTTP_201_CREATED)
def create_service(
    body: ServiceCreateBody,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    name = body.name.strip()
    exists = db.execute(text("SELECT 1 FROM services WHERE LOWER(name) = LOWER(:name)"), {"name": name}).fetchone()
    if exists:
        raise HTTPException(status_code=400, detail="Service name must be unique.")

    st_name = _service_type_name(name, body.billing_type)
    # Ensure unique service type name (rare collision -> append uuid suffix)
    st_exists = db.execute(text("SELECT 1 FROM service_types WHERE name = :n"), {"n": st_name}).fetchone()
    if st_exists:
        st_name = f"{st_name}-{uuid.uuid4().hex[:6]}"

    st_row = db.execute(
        text(
            """
            INSERT INTO service_types (id, name, billing_frequency_days, price, trial_duration_days, is_active)
            VALUES (CAST(:id AS uuid), :name, :days, :price, 3, true)
            RETURNING id
            """
        ),
        {"id": str(uuid.uuid4()), "name": st_name, "days": _billing_to_days(body.billing_type), "price": body.price},
    ).fetchone()

    sv_row = db.execute(
        text(
            """
            INSERT INTO services (id, name, description, service_type_id, is_active)
            VALUES (CAST(:id AS uuid), :name, NULL, CAST(:st_id AS uuid), true)
            RETURNING id
            """
        ),
        {"id": str(uuid.uuid4()), "name": name, "st_id": str(st_row.id)},
    ).fetchone()
    db.commit()

    created = db.execute(
        text("SELECT created_at FROM services WHERE id = CAST(:id AS uuid)"),
        {"id": str(sv_row.id)},
    ).fetchone()
    return {
        "id": str(sv_row.id),
        "name": name,
        "billing_type": body.billing_type,
        "price": float(body.price),
        "total_subscriptions": 0,
        "active_subscriptions": 0,
        "total_campaigns": 0,
        "created_at": created.created_at.isoformat() if created and created.created_at else None,
    }


@router.put("/services/{service_id}")
def update_service(
    service_id: str,
    body: ServiceUpdateBody,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    try:
        sid = str(uuid.UUID(service_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service_id.")

    current = db.execute(
        text(
            """
            SELECT sv.id, sv.name, sv.service_type_id, st.billing_frequency_days, st.price
            FROM services sv
            JOIN service_types st ON st.id = sv.service_type_id
            WHERE sv.id = CAST(:id AS uuid) AND sv.is_active = true
            """
        ),
        {"id": sid},
    ).fetchone()
    if not current:
        raise HTTPException(status_code=404, detail="Service not found.")

    new_name = body.name.strip() if body.name is not None else current.name
    if body.name is not None:
        exists = db.execute(
            text("SELECT 1 FROM services WHERE LOWER(name) = LOWER(:name) AND id <> CAST(:id AS uuid)"),
            {"name": new_name, "id": sid},
        ).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="Service name must be unique.")

    billing_days = int(current.billing_frequency_days or 1)
    current_billing = "daily" if billing_days == 1 else "weekly" if billing_days == 7 else "daily"
    new_billing = body.billing_type or current_billing
    new_price = float(body.price) if body.price is not None else float(current.price or 0)

    new_service_type_id = str(current.service_type_id)
    if new_billing != current_billing or (body.price is not None and new_price != float(current.price or 0)):
        st_name = _service_type_name(new_name, new_billing)
        st_exists = db.execute(text("SELECT 1 FROM service_types WHERE name = :n"), {"n": st_name}).fetchone()
        if st_exists:
            st_name = f"{st_name}-{uuid.uuid4().hex[:6]}"

        st_row = db.execute(
            text(
                """
                INSERT INTO service_types (id, name, billing_frequency_days, price, trial_duration_days, is_active)
                VALUES (CAST(:id AS uuid), :name, :days, :price, 3, true)
                RETURNING id
                """
            ),
            {"id": str(uuid.uuid4()), "name": st_name, "days": _billing_to_days(new_billing), "price": new_price},
        ).fetchone()
        new_service_type_id = str(st_row.id)

    db.execute(
        text(
            """
            UPDATE services
            SET name = :name, service_type_id = CAST(:st_id AS uuid)
            WHERE id = CAST(:id AS uuid)
            """
        ),
        {"id": sid, "name": new_name, "st_id": new_service_type_id},
    )
    db.commit()

    stats = db.execute(
        text(
            """
            SELECT
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = CAST(:id AS uuid)) AS total_subscriptions,
              (SELECT COUNT(*) FROM subscriptions s WHERE s.service_id = CAST(:id AS uuid) AND s.status = 'active') AS active_subscriptions,
              (SELECT COUNT(*) FROM campaigns c WHERE c.service_id = CAST(:id AS uuid)) AS total_campaigns,
              (SELECT created_at FROM services WHERE id = CAST(:id AS uuid)) AS created_at
            """
        ),
        {"id": sid},
    ).fetchone()

    return {
        "id": sid,
        "name": new_name,
        "billing_type": new_billing,
        "price": float(new_price),
        "total_subscriptions": int(stats.total_subscriptions or 0),
        "active_subscriptions": int(stats.active_subscriptions or 0),
        "total_campaigns": int(stats.total_campaigns or 0),
        "created_at": stats.created_at.isoformat() if stats and stats.created_at else None,
    }


@router.delete("/services/{service_id}")
def delete_service(
    service_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    try:
        sid = str(uuid.UUID(service_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service_id.")

    active = db.execute(
        text("SELECT COUNT(*) AS c FROM subscriptions WHERE service_id = CAST(:id AS uuid) AND status = 'active'"),
        {"id": sid},
    ).fetchone()
    active_count = int(active.c or 0)
    if active_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete: service has {active_count} active subscriptions")

    updated = db.execute(
        text("UPDATE services SET is_active = false WHERE id = CAST(:id AS uuid)"),
        {"id": sid},
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found.")
    db.commit()
    return {"success": True}


@router.get("/campaigns")
def list_campaigns(
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    rows = db.execute(
        text(
            """
            SELECT
              c.id,
              c.name,
              c.service_id,
              sv.name AS service_name,
              c.send_datetime,
              c.target_size,
              COUNT(s.id) AS total_subs
            FROM campaigns c
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            LEFT JOIN services sv ON sv.id = c.service_id
            GROUP BY c.id, c.name, c.service_id, sv.name, c.send_datetime, c.target_size
            ORDER BY c.send_datetime DESC
            """
        )
    ).fetchall()

    result = []
    for r in rows:
        conv = (float(r.total_subs or 0) / float(r.target_size or 0) * 100.0) if (r.target_size or 0) else 0.0
        send_dt = r.send_datetime
        if isinstance(send_dt, datetime):
            send_dt = send_dt.astimezone(timezone.utc) if send_dt.tzinfo else send_dt.replace(tzinfo=timezone.utc)
        result.append(
            {
                "id": str(r.id),
                "name": r.name,
                "service_id": str(r.service_id) if r.service_id else None,
                "service_name": r.service_name,
                "send_date": (send_dt.date().isoformat() if send_dt else None),
                "target_size": int(r.target_size or 0),
                "total_subs": int(r.total_subs or 0),
                "conversion_rate": round(conv, 2),
                "status": _campaign_status(send_dt) if send_dt else "scheduled",
            }
        )
    return result


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
def create_campaign(
    body: CampaignCreateBody,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    name = body.name.strip()
    exists = db.execute(text("SELECT 1 FROM campaigns WHERE LOWER(name) = LOWER(:name)"), {"name": name}).fetchone()
    if exists:
        raise HTTPException(status_code=400, detail="Campaign name must be unique.")

    svc = db.execute(text("SELECT 1 FROM services WHERE id = CAST(:id AS uuid) AND is_active = true"), {"id": str(body.service_id)}).fetchone()
    if not svc:
        raise HTTPException(status_code=400, detail="Service does not exist.")

    send_dt = body.send_date
    if send_dt.tzinfo is None:
        send_dt = send_dt.replace(tzinfo=timezone.utc)

    computed_status = _campaign_status(send_dt)
    status_value = "scheduled" if computed_status in ("scheduled", "active") else "completed"

    clean_targets = _sanitize_targets(body.targets)
    effective_target_size = len(clean_targets) if clean_targets else int(body.target_size)

    row = db.execute(
        text(
            """
            INSERT INTO campaigns (
              id, name, description, service_id, send_datetime, target_size, cost, campaign_type, status
            )
            VALUES (
              CAST(:id AS uuid), :name, NULL, CAST(:service_id AS uuid), :send_datetime, :target_size, NULL, :campaign_type, :status
            )
            RETURNING id
            """
        ),
        {
            "id": str(uuid.uuid4()),
            "name": name,
            "service_id": str(body.service_id),
            "send_datetime": send_dt,
            "target_size": effective_target_size,
            "campaign_type": "promotion",
            "status": status_value,
        },
    ).fetchone()

    if clean_targets:
        CampaignRepository.insert_campaign_targets(db, str(row.id), clean_targets)

    db.commit()

    return {
        "id": str(row.id),
        "name": name,
        "service_id": str(body.service_id),
        "service_name": db.execute(text("SELECT name FROM services WHERE id = CAST(:id AS uuid)"), {"id": str(body.service_id)}).scalar(),
        "send_date": send_dt.date().isoformat(),
        "target_size": int(effective_target_size),
        "total_subs": 0,
        "conversion_rate": 0.0,
        "status": computed_status,
    }


@router.put("/campaigns/{campaign_id}")
def update_campaign(
    campaign_id: str,
    body: CampaignUpdateBody,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    try:
        cid = str(uuid.UUID(campaign_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id.")

    current = db.execute(
        text(
            """
            SELECT id, name, service_id, send_datetime, target_size
            FROM campaigns
            WHERE id = CAST(:id AS uuid)
            """
        ),
        {"id": cid},
    ).fetchone()
    if not current:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    new_name = body.name.strip() if body.name is not None else current.name
    if body.name is not None:
        exists = db.execute(
            text("SELECT 1 FROM campaigns WHERE LOWER(name) = LOWER(:name) AND id <> CAST(:id AS uuid)"),
            {"name": new_name, "id": cid},
        ).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="Campaign name must be unique.")

    new_send = body.send_date if body.send_date is not None else current.send_datetime
    if isinstance(new_send, datetime) and new_send.tzinfo is None:
        new_send = new_send.replace(tzinfo=timezone.utc)
    new_target = int(body.target_size) if body.target_size is not None else int(current.target_size or 0)

    computed_status = _campaign_status(new_send) if new_send else "scheduled"
    status_value = "scheduled" if computed_status in ("scheduled", "active") else "completed"

    db.execute(
        text(
            """
            UPDATE campaigns
            SET name = :name,
                send_datetime = :send_datetime,
                target_size = :target_size,
                status = :status
            WHERE id = CAST(:id AS uuid)
            """
        ),
        {"id": cid, "name": new_name, "send_datetime": new_send, "target_size": new_target, "status": status_value},
    )
    db.commit()

    total_subs = db.execute(text("SELECT COUNT(*) FROM subscriptions WHERE campaign_id = CAST(:id AS uuid)"), {"id": cid}).scalar() or 0
    conv = (float(total_subs) / float(new_target) * 100.0) if new_target else 0.0

    return {
        "id": cid,
        "name": new_name,
        "service_id": str(current.service_id) if current.service_id else None,
        "service_name": db.execute(
            text("SELECT name FROM services WHERE id = CAST(:id AS uuid)"),
            {"id": str(current.service_id)},
        ).scalar()
        if current.service_id
        else None,
        "send_date": new_send.date().isoformat() if new_send else None,
        "target_size": int(new_target),
        "total_subs": int(total_subs),
        "conversion_rate": round(conv, 2),
        "status": computed_status,
    }


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    try:
        cid = str(uuid.UUID(campaign_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id.")

    linked = db.execute(
        text("SELECT COUNT(*) AS c FROM subscriptions WHERE campaign_id = CAST(:id AS uuid)"),
        {"id": cid},
    ).fetchone()
    linked_count = int(linked.c or 0)
    if linked_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete: campaign has {linked_count} linked subscriptions")

    deleted = db.execute(text("DELETE FROM campaigns WHERE id = CAST(:id AS uuid)"), {"id": cid}).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    db.commit()
    return {"success": True}

