"""
Segmentation Router — User clustering & behavioral analysis endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.services import segmentation_service
from app.schemas.segmentation import (
    KPIResponse,
    ClustersResponse,
    ProfilesResponse,
    TrainResponse,
)

router = APIRouter(prefix="/analytics/segmentation", tags=["Segmentation"])


@router.get("/kpis", response_model=KPIResponse)
def get_kpis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get KPI metrics for user segmentation.
    
    Returns:
    - total_segments: Number of identified clusters
    - dominant_segment: Segment with highest user count
    - dominant_pct: Percentage of active base in dominant segment
    - high_value_segment: Segment with highest ARPU
    - arpu_premium: ARPU premium vs average (%)
    - risk_segment: Segment with highest churn rate
    - risk_churn_rate: Churn rate of at-risk segment (%)
    """
    start = None
    end = None
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except:
            pass
    
    return segmentation_service.get_segmentation_kpis(db, start, end, service_id)


@router.get("/clusters", response_model=ClustersResponse)
def get_clusters(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get clustering data for 2D visualization.
    
    Returns:
    - clusters: Array of points with (x: activity, y: arpu, segment)
    - distribution: Segment distribution percentages
    """
    start = None
    end = None
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except:
            pass
    
    return segmentation_service.get_segmentation_clusters(db, start, end, service_id)


@router.get("/profiles", response_model=ProfilesResponse)
def get_profiles(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get detailed behavioral profiles for each segment.
    
    Returns profiles with:
    - segment: Segment name
    - avg_duration: Average daily usage duration
    - arpu: Average revenue per user (TND)
    - churn_rate: Estimated churn rate (%)
    """
    start = None
    end = None
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except:
            pass
    
    return segmentation_service.get_segmentation_profiles(db, start, end, service_id)


@router.post("/train", response_model=TrainResponse)
def train_model(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Recalculate the segmentation model using current data.
    
    This clears the cache and forces re-computation of segments
    based on the latest user activity and billing data.
    
    Returns:
    - status: "success" or "error"
    - message: Descriptive message about training
    """
    start = None
    end = None
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except:
            pass
    
    return segmentation_service.train_segmentation_model(db, start, end, service_id)
