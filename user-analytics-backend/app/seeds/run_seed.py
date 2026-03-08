from app.models.platform_users import PlatformUser
from app.models.service_types import ServiceType
from app.models.services import Service
from app.models.users import User
from app.models.campaigns import Campaign
from app.models.subscriptions import Subscription
from app.models.billing_events import BillingEvent
from app.models.unsubscriptions import Unsubscription
from app.models.user_activities import UserActivity
from app.models.sms_events import SmsEvent

from app.seeds.db import get_seed_session
from app.seeds.generators import (
    ServiceTypesGenerator,
    ServicesGenerator,
    UsersGenerator,
    CampaignsGenerator,
    SubscriptionsGenerator,
    SmsGenerator,
    ActivitiesGenerator,
)


def print_summary(db):
    """Affiche un résumé des données en base."""
    counts = {
        "platform_users": db.query(PlatformUser).count(),
        "service_types": db.query(ServiceType).count(),
        "services": db.query(Service).count(),
        "users": db.query(User).count(),
        "campaigns": db.query(Campaign).count(),
        "subscriptions": db.query(Subscription).count(),
        "billing_events": db.query(BillingEvent).count(),
        "unsubscriptions": db.query(Unsubscription).count(),
        "user_activities": db.query(UserActivity).count(),
        "sms_events": db.query(SmsEvent).count(),
    }

    print("\n📊 DONNÉES EN BASE :")
    for table, count in counts.items():
        print(f"   {table:<22} → {count:>7,} lignes".replace(",", " "))

    total = sum(counts.values())
    print(f"\n   {'TOTAL':<22} → {total:>7,} lignes".replace(",", " "))

    print("\n📊 DISTRIBUTION SUBSCRIPTIONS :")
    for status in ["trial", "active", "cancelled"]:
        c = db.query(Subscription).filter(Subscription.status == status).count()
        pct = (c / counts["subscriptions"] * 100) if counts["subscriptions"] > 0 else 0
        print(f"   {status:<15} → {c:>6} ({pct:>5.1f}%)")

    print("\n📊 DISTRIBUTION CHURN :")
    for churn_type in ["VOLUNTARY", "TECHNICAL"]:
        c = (
            db.query(Unsubscription)
            .filter(Unsubscription.churn_type == churn_type)
            .count()
        )
        pct = (
            (c / counts["unsubscriptions"] * 100)
            if counts["unsubscriptions"] > 0
            else 0
        )
        print(f"   {churn_type:<15} → {c:>6} ({pct:>5.1f}%)")


def main():
    print("=" * 70)
    print("🚀 SEEDER RÉALISTE — Analytics Platform")
    print("   Basé sur données réelles ElJournal + Documents projet")
    print("   ⚠️  Platform users créés via /register (pas par le seeder)")
    print("=" * 70)

    db = get_seed_session()

    try:
        # 1. Service Types
        print("\n📊 ÉTAPE 1/7 — Service Types")
        service_types = ServiceTypesGenerator(db).run()

        # 2. Services
        print("\n📱 ÉTAPE 2/7 — Services")
        services = ServicesGenerator(db).run(service_types=service_types)

        # 3. Users
        print("\n👥 ÉTAPE 3/7 — Users")
        users_query = UsersGenerator(db).run()

        # 4. Campaigns
        print("\n📢 ÉTAPE 4/7 — Campaigns")
        campaigns = CampaignsGenerator(db).run(services=services)

        # 5. Subscriptions + Billing + Unsubscriptions
        print("\n🔄 ÉTAPE 5/7 — Subscriptions Ecosystem")
        subs, billings, unsubs = SubscriptionsGenerator(db).run(
            users_query=users_query, services=services, campaigns=campaigns
        )

        # 6. User Activities
        print("\n📈 ÉTAPE 6/7 — User Activities")
        ActivitiesGenerator(db).run(users_query=users_query, services=services)

        # 7. SMS Events
        print("\n💬 ÉTAPE 7/7 — SMS Events")
        SmsGenerator(db).run(users_query=users_query, campaigns=campaigns, services=services)

        # Résumé
        print("\n" + "=" * 70)
        print("✅ GÉNÉRATION TERMINÉE")
        print("=" * 70)
        print_summary(db)

        print("=" * 70)
        print("\n🎉 Données générées avec succès !")
        print("   Lancer l'API : uvicorn app.main:app --reload")
        print("   Swagger UI  : http://localhost:8000/docs")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()