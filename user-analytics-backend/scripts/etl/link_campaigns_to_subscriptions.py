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
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal

def link_campaigns_to_subscriptions():
    """
    Update subscriptions.campaign_id using date+service matching
    """
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("ETL: Link Subscriptions to Campaigns")
        print("=" * 70)
        
        # Count before
        before = db.execute(text(
            "SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL"
        )).scalar()
        print(f"\nBefore: {before} subscriptions with campaign_id")
        
        # Main update: link subscription to closest campaign
        # within 7 days after send_datetime, same service
        update_query = text("""
            UPDATE subscriptions s
            SET campaign_id = (
                SELECT c.id
                FROM campaigns c
                WHERE c.service_id = s.service_id
                  AND s.subscription_start_date BETWEEN
                      c.send_datetime - INTERVAL '1 day'
                      AND c.send_datetime + INTERVAL '7 days'
                ORDER BY ABS(
                    EXTRACT(EPOCH FROM (s.subscription_start_date - c.send_datetime))
                )
                LIMIT 1
            )
            WHERE s.campaign_id IS NULL
              AND s.subscription_start_date >= '2025-10-01'
        """)
        
        result = db.execute(update_query)
        db.commit()
        
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
    link_campaigns_to_subscriptions()
