"""
ETL Script: Link subscriptions to campaigns

Logic:
  - A subscription is linked to a campaign if:
    1. Same service_id
    2. Subscription created within 7 days after campaign send_datetime
    3. We pick the closest campaign temporally
  
This script updates subscriptions.campaign_id to populate the foreign key.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal

def link_campaigns_to_subscriptions(
    start_date: str = "2025-10-01",
    batch_size: int = 20000,
    statement_timeout_ms: int = 0,
):
    """
    Update subscriptions.campaign_id using date+service matching
    """
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("ETL: Link Subscriptions to Campaigns")
        print("=" * 70)

        # Helpful indexes for large-range matching.
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_subscriptions_campaign_null_service_start
            ON subscriptions (service_id, subscription_start_date)
            WHERE campaign_id IS NULL
        """))
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_campaigns_service_send_datetime
            ON campaigns (service_id, send_datetime)
        """))
        db.commit()
        
        # Count before
        before = db.execute(text(
            "SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL"
        )).scalar()
        print(f"\nBefore: {before} subscriptions with campaign_id")
        
        # Process by chunks to avoid statement timeout on big tables.
        update_query = text("""
            WITH candidates AS (
                SELECT s.id, s.service_id, s.subscription_start_date
                FROM subscriptions s
                WHERE s.campaign_id IS NULL
                  AND s.subscription_start_date >= :start_date
                  AND EXISTS (
                      SELECT 1
                      FROM campaigns c
                      WHERE c.service_id = s.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                  )
                ORDER BY s.subscription_start_date
                LIMIT :batch_size
            ),
            matched AS (
                SELECT cand.id AS subscription_id, c_best.id AS campaign_id
                FROM candidates cand
                JOIN LATERAL (
                    SELECT c.id
                    FROM campaigns c
                    WHERE c.service_id = cand.service_id
                      AND cand.subscription_start_date BETWEEN
                          c.send_datetime - INTERVAL '1 day'
                          AND c.send_datetime + INTERVAL '7 days'
                    ORDER BY ABS(
                        EXTRACT(EPOCH FROM (cand.subscription_start_date - c.send_datetime))
                    )
                    LIMIT 1
                ) c_best ON TRUE
            )
            UPDATE subscriptions s
            SET campaign_id = m.campaign_id
            FROM matched m
            WHERE s.id = m.subscription_id
            RETURNING s.id
        """)

        total_linked = 0
        loops = 0
        while True:
            loops += 1
            db.execute(text(f"SET LOCAL statement_timeout = {int(statement_timeout_ms)}"))
            result = db.execute(
                update_query,
                {"start_date": start_date, "batch_size": batch_size},
            )
            updated = len(result.fetchall())
            db.commit()

            if updated == 0:
                break

            total_linked += updated
            print(f"Batch {loops}: +{updated} linked (total +{total_linked})")
        
        # Count after
        after = db.execute(text(
            "SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL"
        )).scalar()
        
        linked = after - before
        print(f"After: {after} subscriptions with campaign_id")
        print(f"Newly linked: {linked}")
        
        # Show distribution by campaign
        print("\nDistribution by campaign:")
        dist = db.execute(text("""
            SELECT c.name, COUNT(s.id) as subs_count
            FROM campaigns c
            LEFT JOIN subscriptions s ON s.campaign_id = c.id
            GROUP BY c.id, c.name
            ORDER BY subs_count DESC
            LIMIT 10
        """)).fetchall()
        
        for campaign_name, count in dist:
            print(f"  {campaign_name}: {count} subscriptions")
        
        print("\n" + "=" * 70)
        print("ETL Complete!")
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\nError during ETL: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Link subscriptions to nearest campaign")
    parser.add_argument("--start-date", type=str, default="2025-10-01", help="Min subscription_start_date")
    parser.add_argument("--batch-size", type=int, default=20000, help="Rows processed per batch")
    parser.add_argument("--statement-timeout-ms", type=int, default=0, help="Postgres statement timeout in ms (0=disabled)")
    args = parser.parse_args()

    link_campaigns_to_subscriptions(
        start_date=args.start_date,
        batch_size=args.batch_size,
        statement_timeout_ms=args.statement_timeout_ms,
    )
