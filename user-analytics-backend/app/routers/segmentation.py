"""
Segmentation Router — User clustering & behavioral analysis endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.cache import cache_invalidate_prefix, cached_endpoint
from app.core.config import settings
from app.core.dependencies import require_admin
from app.services import segmentation_service
from app.schemas.segmentation import (
    KPIResponse,
    ClustersResponse,
    ProfilesResponse,
    TrainResponse,
)

router = APIRouter(prefix="/analytics/segmentation", tags=["Segmentation"])

SEGMENTATION_CACHE_VERSION = "2026-05-05-v5-segmentation-activity-30d"


def _segmentation_cache_payload(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service_id: Optional[str] = None,
    **_: object,
) -> dict:
    return {
        "v": SEGMENTATION_CACHE_VERSION,
        "start_date": start_date or "auto",
        "end_date": end_date or "auto",
        "service_id": service_id or "all",
    }


@router.get("/kpis", response_model=KPIResponse)
@cached_endpoint(
    "segmentation_kpis",
    settings.SEGMENTATION_CACHE_TTL_SECONDS,
    key_builder=_segmentation_cache_payload,
)
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
@cached_endpoint(
    "segmentation_clusters",
    settings.SEGMENTATION_CACHE_TTL_SECONDS,
    key_builder=_segmentation_cache_payload,
)
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
@cached_endpoint(
    "segmentation_profiles",
    settings.SEGMENTATION_CACHE_TTL_SECONDS,
    key_builder=_segmentation_cache_payload,
)
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
    _admin = Depends(require_admin),
):
    """
    Recalculate the segmentation model using current data.
    
    This clears the cache and forces re-computation of segments
    based on the latest user activity and billing data.
    
    Returns:
    - status: "success" or "error"
    - message: Descriptive message about training
    """
    import logging
    logger = logging.getLogger(__name__)
    
    start = None
    end = None
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except Exception as e:
            logger.warning(f"Failed to parse start_date '{start_date}': {e}")
            pass
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except Exception as e:
            logger.warning(f"Failed to parse end_date '{end_date}': {e}")
            pass
    
    try:
        result = segmentation_service.train_segmentation_model(db, start, end, service_id)
        cache_invalidate_prefix("analytics:v2:segmentation_")
        return result
    except Exception as e:
        logger.error(f"Segmentation training failed: {type(e).__name__}: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Training failed: {str(e)[:200]}"
        }
