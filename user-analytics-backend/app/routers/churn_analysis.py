from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.database import get_db
from app.services import churn_service

router = APIRouter(prefix="/analytics/churn", tags=["Churn Analysis"])


@router.get("/dashboard")
def get_churn_dashboard(
    start_date: Optional[datetime] = Query(None),
    end_date:   Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return churn_service.get_churn_dashboard(db, start_date, end_date)


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    from app.repositories import churn_repo
    from app.utils.temporal import get_month_window
    start, end = get_month_window(db)
    return {
        "global_churn_rate":  churn_repo.get_global_churn_rate(db),
        "monthly_churn_rate": churn_repo.get_monthly_churn_rate(db, start, end),
        "avg_lifetime_days":  churn_repo.get_avg_lifetime_days(db),
        "churn_breakdown":    churn_repo.get_churn_breakdown(db),
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
