"""
Runner standalone pour (re)générer uniquement les unsubscriptions.
Usage : python -m app.seeds.run_unsubscriptions_seed
"""
from sqlalchemy import text

from app.models.unsubscriptions import Unsubscription
from app.seeds.db import get_seed_session
from app.seeds.generators.unsubscriptions import UnsubscriptionsGenerator


def truncate_unsubscriptions(db):
    print("Truncate table unsubscriptions...")
    db.execute(text("TRUNCATE TABLE unsubscriptions RESTART IDENTITY CASCADE"))
    db.commit()
    print("  Table vidée OK")


def load_cancelled_subscriptions(db) -> list:
    """
    ✅ Retourne des DICTS — compatible avec UnsubscriptionsGenerator
    qui accède aux données via sub["key"]
    """
    rows = db.execute(text("""
        SELECT
            id,
            user_id,
            service_id,
            subscription_start_date,
            subscription_end_date
        FROM subscriptions
        WHERE status = 'cancelled'
          AND subscription_end_date IS NOT NULL
    """)).fetchall()

    return [
        {
            "id":                       row.id,
            "user_id":                  row.user_id,
            "service_id":               row.service_id,
            "subscription_start_date":  row.subscription_start_date,
            "subscription_end_date":    row.subscription_end_date,
        }
        for row in rows
    ]


def print_stats(db):
    print("\nDISTRIBUTION days_since_subscription (≤ 3 jours — Trial Drop-off) :")
    trial_total = db.query(Unsubscription).filter(
        Unsubscription.days_since_subscription <= 3
    ).count()

    for day in [1, 2, 3]:
        c   = db.query(Unsubscription).filter(
            Unsubscription.days_since_subscription == day
        ).count()
        pct = (c / trial_total * 100) if trial_total > 0 else 0
        label = f"Jour {day}" + (" ZONE CRITIQUE" if day == 3 else "")
        print(f"  {label:<30} → {c:>6} ({pct:>5.1f}%)")

    print(f"  {'TOTAL trial drop-off':<30} → {trial_total:>6}")

    print("\nDISTRIBUTION churn_type :")
    total = db.query(Unsubscription).count()
    for churn_type in ["VOLUNTARY", "TECHNICAL"]:
        c   = db.query(Unsubscription).filter(
            Unsubscription.churn_type == churn_type
        ).count()
        pct = (c / total * 100) if total > 0 else 0
        print(f"  {churn_type:<15} → {c:>6} ({pct:>5.1f}%)")

    print(f"  {'TOTAL':<15} → {total:>6}")


def main():
    print("=" * 60)
    print("UNSUBSCRIPTIONS SEED — Régénération complète")
    print("=" * 60)

    db = get_seed_session()

    try:
        # 1. Truncate
        truncate_unsubscriptions(db)

        # 2. Charger subscriptions cancelled → DICTS
        print("\nChargement subscriptions cancelled...")
        cancelled_subs = load_cancelled_subscriptions(db)
        print(f"  {len(cancelled_subs)} subscriptions chargées")

        if not cancelled_subs:
            print("  Aucune subscription cancelled trouvée. Abandon.")
            return

        # 3. Générer
        print("\nGénération des unsubscriptions...")
        UnsubscriptionsGenerator(db).run(cancelled_subscriptions=cancelled_subs)

        # 4. Stats
        print("\n" + "=" * 60)
        print("GENERATION TERMINEE")
        print("=" * 60)
        print_stats(db)
        print("=" * 60)

    except Exception as e:
        print(f"\nERREUR : {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
