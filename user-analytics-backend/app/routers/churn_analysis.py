import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.database import SessionLocal, get_db
from app.services import churn_service

router = APIRouter(prefix="/analytics/churn", tags=["Churn Analysis"])

_kpis_executor = ThreadPoolExecutor(max_workers=4)


async def _run_in_thread(func):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_kpis_executor, func)


def _kpi_global_churn_rate():
    from app.repositories import churn_repo

    db = SessionLocal()
    try:
        return churn_repo.get_global_churn_rate(db)
    finally:
        db.close()


def _kpi_monthly_churn_rate():
    from app.repositories import churn_repo

    db = SessionLocal()
    try:
        return churn_repo.get_monthly_churn_rate(db)
    finally:
        db.close()


def _kpi_avg_lifetime_days():
    from app.repositories import churn_repo

    db = SessionLocal()
    try:
        return churn_repo.get_avg_lifetime_days(db)
    finally:
        db.close()


def _kpi_churn_breakdown():
    from app.repositories import churn_repo

    db = SessionLocal()
    try:
        return churn_repo.get_churn_breakdown(db)
    finally:
        db.close()


@router.get("/dashboard")
def get_churn_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date:   Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return churn_service.get_churn_dashboard(db, start_date, end_date)


@router.get("/kpis")
async def get_kpis(db: Session = Depends(get_db)):
    _ = db

    global_churn_rate, monthly_churn_rate, avg_lifetime_days, churn_breakdown = await asyncio.gather(
        _run_in_thread(_kpi_global_churn_rate),
        _run_in_thread(_kpi_monthly_churn_rate),
        _run_in_thread(_kpi_avg_lifetime_days),
        _run_in_thread(_kpi_churn_breakdown),
    )

    return {
        "global_churn_rate": global_churn_rate,
        "monthly_churn_rate": monthly_churn_rate,
        "avg_lifetime_days": avg_lifetime_days,
        "churn_breakdown": churn_breakdown,
    }


@router.get("/trend")
def get_trend(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    from app.repositories import churn_repo
    from app.utils.temporal import get_default_window
    start, end = get_default_window(db, days=days)
    return churn_repo.get_churn_trend_daily(db, start, end)


@router.get("/by-service")
def get_by_service(db: Session = Depends(get_db)):
    from app.repositories import churn_repo
    return churn_repo.get_churn_by_service(db)


@router.get("/lifetime")
def get_lifetime(db: Session = Depends(get_db)):
    from app.repositories import churn_repo
    return {
        "stats": churn_repo.get_avg_lifetime_days(db),
        "distribution": churn_repo.get_lifetime_distribution(db),
    }


@router.get("/retention")
def get_retention(db: Session = Depends(get_db)):
    from app.repositories import churn_repo
    return churn_repo.get_retention_cohort(db)
