from app.seeds.db import get_seed_session

from app.models.subscriptions import Subscription

from app.seeds.generators.unsubscriptions import UnsubscriptionsGenerator
from app.seeds.generators.billing_events import BillingGenerator
from sqlalchemy import select


def main():

    print("=" * 60)
    print("🔧 PARTIAL SEED — Billing + Unsubscriptions")
    print("=" * 60)

    db = get_seed_session()

    try:
        # --------------------------------------------------
        # Load existing subscriptions
        # --------------------------------------------------
        print("\n📥 Chargement subscriptions...")
        
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
    

        print(f"   {len(subscriptions)} subscriptions trouvées")

        # --------------------------------------------------
        # Generate Unsubscriptions
        # --------------------------------------------------
        print("\n📉 Génération Unsubscriptions")
        unsubs = UnsubscriptionsGenerator(db).run(
            subscriptions=subscriptions
        )

        # --------------------------------------------------
        # Generate Billing Events
        # --------------------------------------------------
        print("\n💳 Génération Billing Events")
        billings = BillingGenerator(db).run(
            subscriptions=subscriptions
        )

        print("\n✅ PARTIAL SEED TERMINÉ")
        print(f"   Unsubscriptions : {len(unsubs)}")
        print(f"   Billing events  : {len(billings)}")

    except Exception as e:
        print("❌ ERREUR :", e)
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()