"""
Campaign Impact Repository Layer
Provides data access for campaign analytics, impact metrics, and performance analysis
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.sql import bindparam
from typing import List, Dict, Any, Optional
from decimal import Decimal


class CampaignRepository:
    """Repository for campaign analytics queries"""

    @staticmethod
    def get_campaigns_overview(
        db: Session,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        service_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get high-level campaign metrics summary
        Returns total campaigns, by status, total targeted, total subscriptions, conversion rate
        """
        params: Dict[str, Any] = {}
        filters: List[str] = []
        if start_date:
            filters.append("c.send_datetime >= CAST(:start_date AS timestamp)")
            params["start_date"] = start_date
        if end_date:
            filters.append("c.send_datetime < CAST(:end_date AS timestamp) + INTERVAL '1 day'")
            params["end_date"] = end_date
        if service_id:
            filters.append("c.service_id = CAST(:service_id AS uuid)")
            params["service_id"] = service_id
        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""

        result = db.execute(text(f"""
            WITH filtered_campaigns AS (
                SELECT
                    c.id,
                    c.status,
                    c.service_id,
                    c.send_datetime,
                    COALESCE(c.target_size, 0) AS target_size
                FROM campaigns c
                {where_sql}
            ),
            campaign_subs AS (
                SELECT
                    sub.id,
                    fc.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN filtered_campaigns fc ON sub.campaign_id = fc.id

                UNION ALL

                SELECT
                    sub.id,
                    fc.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN filtered_campaigns fc ON fc.service_id = sub.service_id
                WHERE sub.campaign_id IS NULL
                  AND sub.subscription_start_date BETWEEN
                        fc.send_datetime - INTERVAL '1 day'
                        AND fc.send_datetime + INTERVAL '7 days'
            ),
            dedup_subs AS (
                SELECT DISTINCT ON (id, matched_campaign_id)
                    id,
                    matched_campaign_id
                FROM campaign_subs
                ORDER BY id, matched_campaign_id
            ),
            subs_per_campaign AS (
                SELECT
                    matched_campaign_id AS campaign_id,
                    COUNT(DISTINCT id) AS subscriptions
                FROM dedup_subs
                GROUP BY matched_campaign_id
            )
            SELECT
                COUNT(*) AS total_campaigns,
                SUM(CASE WHEN fc.status = 'completed' THEN 1 ELSE 0 END) AS completed_campaigns,
                SUM(CASE WHEN fc.status = 'sent' THEN 1 ELSE 0 END) AS sent_campaigns,
                SUM(CASE WHEN fc.status = 'scheduled' THEN 1 ELSE 0 END) AS scheduled_campaigns,
                COALESCE(SUM(fc.target_size), 0) AS total_targeted,
                COALESCE(SUM(spc.subscriptions), 0) AS total_subscriptions,
                ROUND(
                    (
                        CASE
                            WHEN COALESCE(SUM(fc.target_size), 0) = 0 THEN 0
                            ELSE (COALESCE(SUM(spc.subscriptions), 0)::FLOAT / NULLIF(SUM(fc.target_size), 0)) * 100
                        END
                    )::numeric,
                    2
                ) AS conversion_rate
            FROM filtered_campaigns fc
            LEFT JOIN subs_per_campaign spc ON spc.campaign_id = fc.id
        """), params).fetchone()

        if not result:
            return {
                "total_campaigns": 0,
                "completed_campaigns": 0,
                "sent_campaigns": 0,
                "scheduled_campaigns": 0,
                "total_targeted": 0,
                "total_subscriptions": 0,
                "conversion_rate": 0.0,
            }

        return {
            "total_campaigns": int(result[0]) if result[0] else 0,
            "completed_campaigns": int(result[1]) if result[1] else 0,
            "sent_campaigns": int(result[2]) if result[2] else 0,
            "scheduled_campaigns": int(result[3]) if result[3] else 0,
            "total_targeted": int(result[4]) if result[4] else 0,
            "total_subscriptions": int(result[5]) if result[5] else 0,
            "conversion_rate": float(result[6]) if result[6] else 0.0,
        }

    @staticmethod
    def get_campaign_impact_list(
        db: Session,
        status_filter: Optional[str] = None,
        campaign_type_filter: Optional[str] = None,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        service_id: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get paginated list of campaigns with impact metrics.
        Uses both campaign_id (primary) and date+service (fallback) for subscription matching.
        """
        query = text("""
            WITH campaign_subs AS (
                SELECT
                    sub.id,
                    c.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN campaigns c ON sub.campaign_id = c.id

                UNION ALL

                SELECT
                    sub.id,
                    c.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN campaigns c ON c.service_id = sub.service_id
                WHERE sub.campaign_id IS NULL
                  AND sub.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
            ),
            dedup_subs AS (
                SELECT DISTINCT ON (id, matched_campaign_id)
                    id,
                    matched_campaign_id
                FROM campaign_subs
                ORDER BY id, matched_campaign_id
            )
            SELECT 
                c.id,
                c.name,
                c.description,
                c.campaign_type,
                c.status,
                c.target_size,
                c.cost,
                c.send_datetime,
                COUNT(DISTINCT s.id) as subscriptions_acquired,
                COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0) as first_charges,
                COUNT(DISTINCT b.id) as total_billing_events,
                ROUND(
                    (CASE 
                        WHEN NULLIF(c.target_size, 0) IS NULL THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / c.target_size) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate,
                COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0)::FLOAT / 
                    NULLIF(COUNT(DISTINCT s.id), 0) as first_charge_rate
            FROM campaigns c
            LEFT JOIN dedup_subs s ON s.matched_campaign_id = c.id
            LEFT JOIN billing_events b ON b.subscription_id = s.id
            WHERE 1=1
        """)

        filters: List[str] = []
        params: Dict[str, Any] = {}
        if status_filter and status_filter != "all":
            filters.append("AND c.status = :status_filter")
            params["status_filter"] = status_filter
        if campaign_type_filter and campaign_type_filter != "all":
            filters.append("AND c.campaign_type = :campaign_type_filter")
            params["campaign_type_filter"] = campaign_type_filter
        if start_date:
            filters.append("AND c.send_datetime >= CAST(:start_date AS timestamp)")
            params["start_date"] = start_date
        if end_date:
            filters.append("AND c.send_datetime < CAST(:end_date AS timestamp) + INTERVAL '1 day'")
            params["end_date"] = end_date
        if service_id:
            filters.append("AND c.service_id = CAST(:service_id AS uuid)")
            params["service_id"] = service_id

        filter_str = " ".join(filters)
        
        # Get total count first
        count_query = text(f"""
            SELECT COUNT(DISTINCT c.id)
            FROM campaigns c
            WHERE 1=1 {filter_str}
        """)
        
        total_count = db.execute(count_query, params).scalar() or 0
        
        # Get paginated data
        offset = (page - 1) * limit
        full_query = query.text + f"""
            {filter_str}
            GROUP BY c.id, c.name, c.description, c.campaign_type, c.status, c.target_size, c.cost, c.send_datetime
            ORDER BY c.send_datetime DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """
        
        params["limit"] = limit
        params["offset"] = offset
        results = db.execute(text(full_query), params).fetchall()
        
        campaigns = []
        for row in results:
            first_charge_rate = row[12]
            if first_charge_rate is None or (isinstance(first_charge_rate, float) and row[9] == 0):
                first_charge_rate = 0.0
            else:
                first_charge_rate = float(first_charge_rate) * 100
            
            campaigns.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "campaign_type": row[3],
                "status": row[4],
                "target_size": int(row[5]) if row[5] else 0,
                "cost": float(row[6]) if row[6] else 0.0,
                "send_datetime": row[7].isoformat() if row[7] else None,
                "subscriptions_acquired": int(row[8]) if row[8] else 0,
                "first_charges": int(row[9]) if row[9] else 0,
                "total_billing_events": int(row[10]) if row[10] else 0,
                "conversion_rate": float(row[11]) if row[11] else 0.0,
                "first_charge_rate": first_charge_rate,
            })

        return {
            "campaigns": campaigns,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": (total_count + limit - 1) // limit if total_count > 0 else 0,
        }

    @staticmethod
    def get_impact_by_type(
        db: Session,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        service_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get campaign impact aggregated by campaign_type.
        Uses both campaign_id (primary) and date+service (fallback) for subscription matching.
        """
        params: Dict[str, Any] = {}
        filters: List[str] = []
        if start_date:
            filters.append("c.send_datetime >= CAST(:start_date AS timestamp)")
            params["start_date"] = start_date
        if end_date:
            filters.append("c.send_datetime < CAST(:end_date AS timestamp) + INTERVAL '1 day'")
            params["end_date"] = end_date
        if service_id:
            filters.append("c.service_id = CAST(:service_id AS uuid)")
            params["service_id"] = service_id
        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""

        result = db.execute(text(f"""
            WITH filtered_campaigns AS (
                SELECT
                    c.id,
                    c.campaign_type,
                    c.service_id,
                    c.send_datetime,
                    COALESCE(c.target_size, 0) AS target_size
                FROM campaigns c
                {where_sql}
            ),
            campaign_subs AS (
                SELECT
                    sub.id,
                    fc.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN filtered_campaigns fc ON sub.campaign_id = fc.id

                UNION ALL

                SELECT
                    sub.id,
                    fc.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN filtered_campaigns fc ON fc.service_id = sub.service_id
                WHERE sub.campaign_id IS NULL
                  AND sub.subscription_start_date BETWEEN
                        fc.send_datetime - INTERVAL '1 day'
                        AND fc.send_datetime + INTERVAL '7 days'
            ),
            dedup_subs AS (
                SELECT DISTINCT ON (id, matched_campaign_id)
                    id,
                    matched_campaign_id
                FROM campaign_subs
                ORDER BY id, matched_campaign_id
            ),
            per_campaign AS (
                SELECT
                    fc.id,
                    fc.campaign_type,
                    fc.target_size,
                    COUNT(DISTINCT ds.id) AS subscriptions,
                    COUNT(DISTINCT b.id) AS billing_events,
                    COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0) AS first_charges
                FROM filtered_campaigns fc
                LEFT JOIN dedup_subs ds ON ds.matched_campaign_id = fc.id
                LEFT JOIN billing_events b ON b.subscription_id = ds.id
                GROUP BY fc.id, fc.campaign_type, fc.target_size
            )
            SELECT
                campaign_type,
                COUNT(*) AS count,
                SUM(target_size) AS targeted,
                SUM(subscriptions) AS subscriptions,
                SUM(billing_events) AS billing_events,
                SUM(first_charges) AS first_charges,
                ROUND(
                    (
                        CASE
                            WHEN NULLIF(SUM(target_size), 0) IS NULL THEN 0
                            ELSE (SUM(subscriptions)::FLOAT / SUM(target_size)) * 100
                        END
                    )::numeric,
                    2
                ) AS conversion_rate
            FROM per_campaign
            GROUP BY campaign_type
            ORDER BY COUNT(*) DESC
        """), params).fetchall()

        types_data = []
        for row in result:
            types_data.append({
                "type": row[0] or "unknown",
                "campaign_count": int(row[1]) if row[1] else 0,
                "targeted": int(row[2]) if row[2] else 0,
                "subscriptions": int(row[3]) if row[3] else 0,
                "billing_events": int(row[4]) if row[4] else 0,
                "first_charges": int(row[5]) if row[5] else 0,
                "conversion_rate": float(row[6]) if row[6] else 0.0,
            })

        return types_data

    @staticmethod
    def get_top_campaigns(
        db: Session,
        limit: int = 5,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        service_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get top N campaigns by conversion rate (or subscriptions acquired if rate is 0)
        Uses both campaign_id (primary) and date+service (fallback) for subscription matching.
        """
        params: Dict[str, Any] = {"limit": limit}
        filters: List[str] = []
        if start_date:
            filters.append("c.send_datetime >= CAST(:start_date AS timestamp)")
            params["start_date"] = start_date
        if end_date:
            filters.append("c.send_datetime < CAST(:end_date AS timestamp) + INTERVAL '1 day'")
            params["end_date"] = end_date
        if service_id:
            filters.append("c.service_id = CAST(:service_id AS uuid)")
            params["service_id"] = service_id
        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""

        result = db.execute(text(f"""
            WITH campaign_subs AS (
                SELECT
                    sub.id,
                    c.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN campaigns c ON sub.campaign_id = c.id

                UNION ALL

                SELECT
                    sub.id,
                    c.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN campaigns c ON c.service_id = sub.service_id
                WHERE sub.campaign_id IS NULL
                  AND sub.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
            ),
            dedup_subs AS (
                SELECT DISTINCT ON (id, matched_campaign_id)
                    id,
                    matched_campaign_id
                FROM campaign_subs
                ORDER BY id, matched_campaign_id
            )
            SELECT 
                c.id,
                c.name,
                c.campaign_type,
                c.target_size,
                COUNT(DISTINCT s.id) as subscriptions,
                ROUND(
                    (CASE 
                        WHEN NULLIF(c.target_size, 0) IS NULL THEN 0
                        ELSE (COUNT(DISTINCT s.id)::FLOAT / c.target_size) * 100
                    END)::numeric, 
                    2
                ) as conversion_rate
            FROM campaigns c
            LEFT JOIN dedup_subs s ON s.matched_campaign_id = c.id
            {where_sql}
            GROUP BY c.id, c.name, c.campaign_type, c.target_size
            ORDER BY conversion_rate DESC NULLS LAST, subscriptions DESC NULLS LAST
            LIMIT :limit
        """), params).fetchall()

        top_campaigns = []
        for row in result:
            top_campaigns.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "targeted": int(row[3]) if row[3] else 0,
                "subscriptions": int(row[4]) if row[4] else 0,
                "conversion_rate": float(row[5]) if row[5] else 0.0,
            })

        return top_campaigns

    @staticmethod
    def get_campaigns_monthly_trend(
        db: Session,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        service_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get campaign metrics aggregated by month (based on send_datetime)
        Uses both campaign_id (primary) and date+service (fallback) for subscription matching.
        """
        params: Dict[str, Any] = {}
        filters: List[str] = ["c.send_datetime IS NOT NULL"]
        if start_date:
            filters.append("c.send_datetime >= CAST(:start_date AS timestamp)")
            params["start_date"] = start_date
        if end_date:
            filters.append("c.send_datetime < CAST(:end_date AS timestamp) + INTERVAL '1 day'")
            params["end_date"] = end_date
        if service_id:
            filters.append("c.service_id = CAST(:service_id AS uuid)")
            params["service_id"] = service_id
        where_sql = f"WHERE {' AND '.join(filters)}"

        result = db.execute(text(f"""
            WITH filtered_campaigns AS (
                SELECT
                    c.id,
                    DATE_TRUNC('month', c.send_datetime)::DATE AS month,
                    c.campaign_type,
                    c.service_id,
                    c.send_datetime,
                    COALESCE(c.target_size, 0) AS target_size
                FROM campaigns c
                {where_sql}
            ),
            campaign_subs AS (
                SELECT
                    sub.id,
                    fc.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN filtered_campaigns fc ON sub.campaign_id = fc.id

                UNION ALL

                SELECT
                    sub.id,
                    fc.id AS matched_campaign_id
                FROM subscriptions sub
                JOIN filtered_campaigns fc ON fc.service_id = sub.service_id
                WHERE sub.campaign_id IS NULL
                  AND sub.subscription_start_date BETWEEN
                        fc.send_datetime - INTERVAL '1 day'
                        AND fc.send_datetime + INTERVAL '7 days'
            ),
            dedup_subs AS (
                SELECT DISTINCT ON (id, matched_campaign_id)
                    id,
                    matched_campaign_id
                FROM campaign_subs
                ORDER BY id, matched_campaign_id
            ),
            per_campaign AS (
                SELECT
                    fc.id,
                    fc.month,
                    fc.campaign_type,
                    fc.target_size,
                    COUNT(DISTINCT ds.id) AS subscriptions,
                    COALESCE(SUM(CASE WHEN b.is_first_charge THEN 1 ELSE 0 END), 0) AS first_charges
                FROM filtered_campaigns fc
                LEFT JOIN dedup_subs ds ON ds.matched_campaign_id = fc.id
                LEFT JOIN billing_events b ON b.subscription_id = ds.id
                GROUP BY fc.id, fc.month, fc.campaign_type, fc.target_size
            )
            SELECT
                month,
                campaign_type,
                COUNT(*) AS campaign_count,
                SUM(target_size) AS targeted,
                SUM(subscriptions) AS subscriptions,
                SUM(first_charges) AS first_charges,
                ROUND(
                    (
                        CASE
                            WHEN NULLIF(SUM(target_size), 0) IS NULL THEN 0
                            ELSE (SUM(subscriptions)::FLOAT / SUM(target_size)) * 100
                        END
                    )::numeric,
                    2
                ) AS conversion_rate
            FROM per_campaign
            GROUP BY month, campaign_type
            ORDER BY month DESC
        """), params).fetchall()

        monthly_data = []
        for row in result:
            monthly_data.append({
                "month": row[0].isoformat() if row[0] else None,
                "campaign_type": row[1] or "unknown",
                "campaign_count": int(row[2]) if row[2] else 0,
                "targeted": int(row[3]) if row[3] else 0,
                "subscriptions": int(row[4]) if row[4] else 0,
                "first_charges": int(row[5]) if row[5] else 0,
                "conversion_rate": float(row[6]) if row[6] else 0.0,
            })

        return monthly_data

    @staticmethod
    def insert_campaign_targets(
        db: Session,
        campaign_id: str,
        targets: List[Dict[str, Any]],
    ) -> int:
        """Bulk insert targets for one campaign, ignoring duplicates on (campaign_id, phone_number)."""
        if not targets:
            return 0

        payload = []
        for row in targets:
            payload.append(
                {
                    "campaign_id": campaign_id,
                    "phone_number": str(row.get("phone_number", "")).strip(),
                    "segment": (str(row.get("segment", "")).strip() or None),
                    "region": (str(row.get("region", "")).strip() or None),
                }
            )

        stmt = text(
            """
            INSERT INTO campaign_targets (campaign_id, phone_number, segment, region)
            VALUES (CAST(:campaign_id AS uuid), :phone_number, :segment, :region)
            ON CONFLICT (campaign_id, phone_number) DO NOTHING
            """
        )

        result = db.execute(stmt, payload)
        return int(result.rowcount or 0)
