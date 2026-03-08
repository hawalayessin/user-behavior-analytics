from sqlalchemy import select, text

from app.seeds.db import get_seed_session
from app.models.subscriptions import Subscription
from app.seeds.generators.billing_events import BillingGenerator


def main():
    print("=" * 60)
    print("BILLING EVENTS SEED")
    print("=" * 60)

    db = get_seed_session()

    try:
        # ✅ Truncate avant re-run
        print("Nettoyage table billing_events...")
        db.execute(text("TRUNCATE TABLE billing_events RESTART IDENTITY CASCADE"))
        db.commit()
        print("  Table vidée OK")

        print("\nChargement subscriptions...")
        result = db.execute(
            select(
                Subscription.id,
                Subscription.user_id,
                Subscription.service_id,
                Subscription.subscription_start_date,
                Subscription.subscription_end_date,
                Subscription.status,
            )
        )
        subscriptions = result.all()
        print(f"  {len(subscriptions)} subscriptions trouvées")

        print("\nGénération Billing Events...")
        billings = BillingGenerator(db).run(subscriptions=subscriptions)

        print("\nBILLING TERMINE")
        print(f"  Billing events créés : {len(billings)}")

        # ── Vérification ──────────────────────────────────────────────────
        print("\nDistribution status billing :")
        r1 = db.execute(text("""
            SELECT status, COUNT(*) AS total,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
            FROM billing_events
            GROUP BY status
            ORDER BY total DESC
        """))
        for row in r1.fetchall():
            print(f"  {row[0]:<10} : {row[1]:>8}  ({row[2]}%)")

        print("\nBilling events par service :")
        r2 = db.execute(text("""
            SELECT srv.name, COUNT(*) AS total
            FROM billing_events be
            JOIN services srv ON srv.id = be.service_id
            GROUP BY srv.name
            ORDER BY total DESC
        """))
        for row in r2.fetchall():
            print(f"  {row[0]:<20} : {row[1]:>8}")

    except Exception as e:
        print("\nERREUR :", e)
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
