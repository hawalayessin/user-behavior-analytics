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

	total_targeted = float(kpis.get("total_targeted") or 0)
	qualified_targeted = float(kpis.get("qualified_targeted") or 0)
	total_messages_sent = float(kpis.get("total_messages_sent") or 0)
	total_messages_delivered = float(kpis.get("total_messages_delivered") or 0)

	target_coverage_pct = round((qualified_targeted * 100.0 / total_targeted), 1) if total_targeted > 0 else 0.0
	sms_coverage_pct = round((total_messages_sent * 100.0 / total_targeted), 1) if total_targeted > 0 else 0.0
	delivery_success_pct = round((total_messages_delivered * 100.0 / total_messages_sent), 1) if total_messages_sent > 0 else 0.0

	quality_score = round((0.45 * target_coverage_pct) + (0.25 * min(sms_coverage_pct, 100.0)) + (0.30 * delivery_success_pct), 1)
	if quality_score >= 85:
		quality_status = "excellent"
	elif quality_score >= 70:
		quality_status = "good"
	elif quality_score >= 50:
		quality_status = "fair"
	else:
		quality_status = "poor"

	return {
		"kpis": kpis,
		"data_quality": {
			"quality_score": quality_score,
			"quality_status": quality_status,
			"target_coverage_pct": target_coverage_pct,
			"sms_coverage_pct": sms_coverage_pct,
			"delivery_success_pct": delivery_success_pct,
			"quality_formula": "0.45*target_coverage+0.25*min(sms_coverage,100)+0.30*delivery_success",
		},
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
