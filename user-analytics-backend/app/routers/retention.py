from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.date_ranges import DATA_START_DATE, resolve_date_range
from app.core.cache import cached_endpoint
from app.core.config import settings
from app.models.cohorts import Cohort
from app.models.services import Service


router = APIRouter(prefix="/analytics", tags=["Retention"])


def _retention_range_payload(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service_id: Optional[str] = None,
    **_: object,
) -> dict:
    return {
        "start_date": start_date.isoformat() if start_date else DATA_START_DATE.isoformat(),
        "end_date": end_date.isoformat() if end_date else "auto",
        "service_id": service_id or "all",
    }


def _retention_heatmap_payload(
    service_id: Optional[str] = None,
    last_n_months: int = 6,
    **_: object,
) -> dict:
    return {
        "service_id": service_id or "all",
        "last_n_months": int(last_n_months),
    }


def _retention_cohorts_payload(
    service_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    **_: object,
) -> dict:
    return {
        "service_id": service_id or "all",
        "page": int(page),
        "page_size": int(page_size),
    }


def _parse_date_range(
    start_date: Optional[date],
    end_date: Optional[date],
    *,
    db: Session,
) -> tuple[date, date]:
    _ = db
    return resolve_date_range(start_date, end_date)


@router.get("/retention/kpis")
@cached_endpoint(
    "retention_kpis",
    settings.RETENTION_CACHE_TTL_SECONDS,
    key_builder=_retention_range_payload,
)
def get_retention_kpis(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=DATA_START_DATE),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _parse_date_range(start_date, end_date, db=db)

    query = (
        db.query(
            func.avg(Cohort.retention_d7).label("avg_d7"),
            func.avg(Cohort.retention_d30).label("avg_d30"),
            func.count(Cohort.id).label("total_cohorts"),
        )
        .filter(Cohort.cohort_date >= start_dt, Cohort.cohort_date <= end_dt)
    )

    if service_id:
        query = query.filter(Cohort.service_id == service_id)

    agg = query.one()

    best_row = (
        db.query(
            Cohort.cohort_date,
            Cohort.retention_d7,
        )
        .filter(Cohort.cohort_date >= start_dt, Cohort.cohort_date <= end_dt)
        .order_by(Cohort.retention_d7.desc().nullslast())
        .first()
    )

    at_risk_count = (
        db.query(func.count(Cohort.id))
        .filter(
            Cohort.cohort_date >= start_dt,
            Cohort.cohort_date <= end_dt,
            Cohort.retention_d7.isnot(None),
            Cohort.retention_d7 < 30,
        )
        .scalar()
    )

    return {
        "avg_retention_d7": float(agg.avg_d7 or 0),
        "avg_retention_d30": float(agg.avg_d30 or 0),
        "best_cohort": best_row.cohort_date.strftime("%Y-%m") if best_row else None,
        "best_cohort_d7": float(best_row.retention_d7 or 0) if best_row else 0,
        "at_risk_count": int(at_risk_count or 0),
        "total_cohorts": int(agg.total_cohorts or 0),
    }


@router.get("/retention/heatmap")
@cached_endpoint(
    "retention_heatmap",
    settings.RETENTION_CACHE_TTL_SECONDS,
    key_builder=_retention_heatmap_payload,
)
def get_retention_heatmap(
    db: Session = Depends(get_db),
    service_id: Optional[str] = Query(default=None),
    last_n_months: int = Query(default=6, ge=1, le=24),
):
    end_dt = date.today()
    start_dt = end_dt.replace(day=1) - timedelta(days=last_n_months * 30)

    query = (
        db.query(
            Cohort.cohort_date,
            Service.name.label("service_name"),
            Cohort.total_users,
            Cohort.retention_d7,
            Cohort.retention_d14,
            Cohort.retention_d30,
        )
        .join(Service, Cohort.service_id == Service.id)
        .filter(Cohort.cohort_date >= start_dt, Cohort.cohort_date <= end_dt)
    )

    if service_id:
        query = query.filter(Cohort.service_id == service_id)

    rows = query.order_by(Cohort.cohort_date.desc(), Service.name).all()

    data = [
        {
            "cohort": row.cohort_date.strftime("%Y-%m"),
            "service": row.service_name,
            "total_users": int(row.total_users or 0),
            "d7": float(row.retention_d7 or 0),
            "d14": float(row.retention_d14 or 0),
            "d30": float(row.retention_d30 or 0),
        }
        for row in rows
    ]

    return {"data": data}


@router.get("/retention/curve")
@cached_endpoint(
    "retention_curve",
    settings.RETENTION_CACHE_TTL_SECONDS,
    key_builder=_retention_range_payload,
)
def get_retention_curve(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=DATA_START_DATE),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _parse_date_range(start_date, end_date, db=db)

    query = (
        db.query(
            Service.name.label("service_name"),
            func.avg(Cohort.retention_d7).label("avg_d7"),
            func.avg(Cohort.retention_d14).label("avg_d14"),
            func.avg(Cohort.retention_d30).label("avg_d30"),
        )
        .join(Service, Cohort.service_id == Service.id)
        .filter(Cohort.cohort_date >= start_dt, Cohort.cohort_date <= end_dt)
        .group_by(Service.id, Service.name)
    )

    if service_id:
        query = query.filter(Cohort.service_id == service_id)

    rows = query.order_by(Service.name).all()

    data = [
        {
            "service": row.service_name,
            "d0": 100.0,
            "d7": float(row.avg_d7 or 0),
            "d14": float(row.avg_d14 or 0),
            "d30": float(row.avg_d30 or 0),
        }
        for row in rows
    ]

    return {"data": data}


@router.get("/retention/cohorts-list")
@cached_endpoint(
    "retention_cohorts_list",
    settings.RETENTION_CACHE_TTL_SECONDS,
    key_builder=_retention_cohorts_payload,
)
def get_retention_cohorts_list(
    db: Session = Depends(get_db),
    service_id: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    base_query = (
        db.query(
            Cohort.cohort_date,
            Cohort.total_users,
            Cohort.retention_d7,
            Cohort.retention_d14,
            Cohort.retention_d30,
            Service.name.label("service_name"),
        )
        .join(Service, Cohort.service_id == Service.id)
    )

    if service_id:
        base_query = base_query.filter(Cohort.service_id == service_id)

    total = base_query.count()

    rows = (
        base_query.order_by(Cohort.cohort_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    def _health(d7: Optional[float]) -> str:
        if d7 is None:
            return "critical"
        v = float(d7)
        if v >= 40:
            return "good"
        if v >= 20:
            return "warning"
        return "critical"

    data = [
        {
            "cohort_date": row.cohort_date.isoformat(),
            "service_name": row.service_name,
            "total_users": int(row.total_users or 0),
            "retention_d7": float(row.retention_d7 or 0),
            "retention_d14": float(row.retention_d14 or 0),
            "retention_d30": float(row.retention_d30 or 0),
            "health": _health(row.retention_d7),
        }
        for row in rows
    ]

    return {
        "data": data,
        "total": total,
        "page": page,
    }

