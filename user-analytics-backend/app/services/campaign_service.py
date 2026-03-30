"""
Campaign Impact Service Layer
Business logic for campaign analytics with caching
"""

from sqlalchemy.orm import Session
from app.repositories.campaign_repo import CampaignRepository
from typing import Any, Dict, Optional
from datetime import date, datetime


# Simple in-memory cache for campaign data (30 second TTL)
_campaign_cache = {}
_cache_timestamps = {}
CACHE_TTL = 30


def _get_cache_key(cache_type: str, **kwargs) -> str:
    """Generate cache key from parameters"""
    parts = [cache_type]
    for key in sorted(kwargs.keys()):
        parts.append(f"{key}={kwargs[key]}")
    return "|".join(parts)


def _is_cache_valid(key: str) -> bool:
    """Check if cache entry is still valid"""
    if key not in _cache_timestamps:
        return False
    elapsed = (datetime.now() - _cache_timestamps[key]).total_seconds()
    return elapsed < CACHE_TTL


def _get_cached(key: str) -> Optional[Any]:
    """Get value from cache if valid"""
    if _is_cache_valid(key):
        return _campaign_cache.get(key)
    return None


def _set_cache(key: str, value: Any):
    """Store value in cache with timestamp"""
    _campaign_cache[key] = value
    _cache_timestamps[key] = datetime.now()


def get_campaign_dashboard(db: Session, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get complete campaign impact dashboard in a single payload
    Combines overview, type breakdown, monthly trend, and top campaigns
    
    Args:
        db: Database session
        filters: Optional dict with start_date, end_date, service_id
    """
    if filters is None:
        filters = {}
    
    # Generate cache key from filters
    cache_key = _get_cache_key(
        "campaign_dashboard",
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date"),
        service_id=filters.get("service_id"),
    )
    
    cached = _get_cached(cache_key)
    if cached:
        return cached

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    service_id = filters.get("service_id")

    overview = CampaignRepository.get_campaigns_overview(
        db,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
    )
    by_type = CampaignRepository.get_impact_by_type(
        db,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
    )
    monthly_trend = CampaignRepository.get_campaigns_monthly_trend(
        db,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
    )
    top_campaigns = CampaignRepository.get_top_campaigns(
        db,
        limit=5,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
    )

    response = {
        "kpis": {
            "total_campaigns": overview["total_campaigns"],
            "total_targeted": overview["total_targeted"],
            "total_subscriptions": overview["total_subscriptions"],
            "conversion_rate": overview["conversion_rate"],
        },
        "charts": {
            "by_type": by_type,
            "monthly_trend": monthly_trend,
            "top_campaigns": top_campaigns,
        },
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "cache_ttl_seconds": CACHE_TTL,
            "filters_applied": {
                "start_date": filters.get("start_date"),
                "end_date": filters.get("end_date"),
                "service_id": filters.get("service_id"),
            },
        },
    }

    _set_cache(cache_key, response)
    return response


def get_campaign_list(
    db: Session,
    status_filter: Optional[str] = None,
    campaign_type_filter: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service_id: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Get paginated campaign list with impact metrics and filtering
    """
    # Don't cache list endpoints as they're paginated
    return CampaignRepository.get_campaign_impact_list(
        db,
        status_filter=status_filter,
        campaign_type_filter=campaign_type_filter,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
        page=page,
        limit=limit,
    )
