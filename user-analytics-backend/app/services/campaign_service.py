"""Campaign service layer.

Provides orchestration functions used by campaign routers.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.repositories.campaign_repo import CampaignRepository


def get_campaign_dashboard(
	db: Session,
	*,
	filters: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
	"""Return campaign dashboard payload consumed by frontend."""
	f = filters or {}
	start_date = f.get("start_date")
	end_date = f.get("end_date")
	service_id = f.get("service_id")

	kpis = CampaignRepository.get_campaigns_overview(
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

	return {
		"kpis": kpis,
		"charts": {
			"by_type": by_type,
			"monthly_trend": monthly_trend,
			"top_campaigns": top_campaigns,
		},
	}


def get_campaign_list(
	db: Session,
	*,
	status_filter: Optional[str] = None,
	campaign_type_filter: Optional[str] = None,
	start_date: Optional[Any] = None,
	end_date: Optional[Any] = None,
	service_id: Optional[str] = None,
	page: int = 1,
	limit: int = 10,
) -> dict[str, Any]:
	"""Return paginated campaign list with impact metrics."""
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
