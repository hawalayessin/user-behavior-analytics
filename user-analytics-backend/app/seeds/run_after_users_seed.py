"""
Régénère toutes les tables dépendantes des users (après run_users_seed).
Usage : python -m app.seeds.run_after_users_seed

Ordre :
  1. Subscriptions  (dépend de users, services, campaigns)
  2. Billing Events (dépend de subscriptions)
  3. Unsubscriptions(dépend de subscriptions)
  4. User Activities(dépend de users, services)
  5. SMS Events     (dépend de users, campaigns, services)
"""
from sqlalchemy import text
from app.seeds.db import get_seed_session
from app.seeds.generators.subscriptions import SubscriptionsGenerator
from app.seeds.generators.activities import ActivitiesGenerator
from app.seeds.generators.sms import SmsGenerator
from app.seeds.generators.unsubscriptions import UnsubscriptionsGenerator


# ─────────────────────────────────────────────
# Helpers chargement raw SQL
# ─────────────────────────────────────────────

def load_services(db) -> list:
    rows = db.execute(text("SELECT id::text, name FROM services")).fetchall()
    return [{"id": row[0], "name": row[1]} for row in rows]


def load_campaigns(db) -> list:
    rows = db.execute(text("SELECT id::text, name FROM campaigns")).fetchall()
    return [{"id": row[0], "name": row[1]} for row in rows]


def load_cancelled_subscriptions(db) -> list:
    rows = db.execute(text("""
        SELECT
            id::text,
            user_id::text,
            service_id::text,
            subscription_start_date,
            subscription_end_date
        FROM subscriptions
        WHERE status = 'cancelled'
          AND subscription_end_date IS NOT NULL
    """)).fetchall()
    return [
        {
            "id":                      row[0],
            "user_id":                 row[1],
            "service_id":              row[2],
            "subscription_start_date": row[3],
            "subscription_end_date":   row[4],
        }
        for row in rows
    ]


# ─────────────────────────────────────────────
# Truncate tables dépendantes (pas users)
# ─────────────────────────────────────────────

def truncate_dependent_tables(db):
    print("🗑️  Truncate tables dépendantes...")
    db.execute(text("""
        TRUNCATE TABLE
            sms_events,
            user_activities,
            unsubscriptions,
            billing_events,
            subscriptions
        RESTART IDENTITY CASCADE
    """))
    db.commit()
    print("   ✅ Tables vidées.")


# ─────────────────────────────────────────────
# Stats finales
# ─────────────────────────────────────────────

def print_summary(db):
    tables = [
        "users",
        "subscriptions",
        "billing_events",
        "unsubscriptions",
        "user_activities",
        "sms_events",
    ]

    print("\n📊 DONNÉES EN BASE :")
    total = 0
    for table in tables:
        c = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        total += c
        print(f"   {table:<22} → {c:>7,} lignes".replace(",", " "))
    print(f"\n   {'TOTAL':<22} → {total:>7,} lignes".replace(",", " "))

    print("\n📊 DISTRIBUTION SUBSCRIPTIONS :")
    sub_total = db.execute(text("SELECT COUNT(*) FROM subscriptions")).scalar()
    for status in ["trial", "active", "cancelled"]:
        c   = db.execute(text(
            "SELECT COUNT(*) FROM subscriptions WHERE status = :s"
        ), {"s": status}).scalar()
        pct = (c / sub_total * 100) if sub_total > 0 else 0
        print(f"   {status:<15} → {c:>6} ({pct:>5.1f}%)")

    print("\n📊 DISTRIBUTION CHURN :")
    unsub_total = db.execute(text("SELECT COUNT(*) FROM unsubscriptions")).scalar()
    for ct in ["VOLUNTARY", "TECHNICAL"]:
        c   = db.execute(text(
            "SELECT COUNT(*) FROM unsubscriptions WHERE churn_type = :ct"
        ), {"ct": ct}).scalar()
        pct = (c / unsub_total * 100) if unsub_total > 0 else 0
        print(f"   {ct:<15} → {c:>6} ({pct:>5.1f}%)")

    print("\n📊 TRIAL DROP-OFF (J1/J2/J3) :")
    trial_total = db.execute(text(
        "SELECT COUNT(*) FROM unsubscriptions WHERE days_since_subscription <= 3"
    )).scalar()
    for day in [1, 2, 3]:
        c   = db.execute(text(
            "SELECT COUNT(*) FROM unsubscriptions WHERE days_since_subscription = :d"
        ), {"d": day}).scalar()
        pct = (c / trial_total * 100) if trial_total > 0 else 0
        print(f"   Jour {day:<11} → {c:>6} ({pct:>5.1f}%)")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=" * 70)
    print("🔄 AFTER-USERS SEED — Régénération tables dépendantes")
    print("=" * 70)

    db = get_seed_session()

    try:
        # 0. Vérifier que les users existent
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if user_count == 0:
            print("❌ Aucun user en base. Lancez d'abord run_users_seed.")
            return
        print(f"✅ {user_count:,} users trouvés.".replace(",", " "))

        # 0b. Charger services & campaigns (raw SQL)
        services  = load_services(db)
        campaigns = load_campaigns(db)
        print(f"✅ {len(services)} services / {len(campaigns)} campaigns chargés.")

        if not services:
            print("❌ Aucun service en base. Lancez d'abord run_seed complet.")
            return

        # 1. Truncate
        truncate_dependent_tables(db)

        # 2. Subscriptions
        print("\n🔄 ÉTAPE 1/4 — Subscriptions...")
        users_query = db.query(__import__('app.models.users', fromlist=['User']).User)
        subs, _, _ = SubscriptionsGenerator(db).run(
            users_query=users_query,
            services=services,
            campaigns=campaigns,
        )
        print(f"   ✅ {len(subs):,} subscriptions créées.".replace(",", " "))

        # 3. Unsubscriptions
        print("\n🔄 ÉTAPE 2/4 — Unsubscriptions...")
        cancelled = load_cancelled_subscriptions(db)
        print(f"   {len(cancelled):,} subscriptions cancelled trouvées.".replace(",", " "))
        if cancelled:
            UnsubscriptionsGenerator(db).run(cancelled_subscriptions=cancelled)

        # 4. User Activities
        print("\n🔄 ÉTAPE 3/4 — User Activities...")
        ActivitiesGenerator(db).run(
            users_query=users_query,
            services=services,
        )

        # 5. SMS Events
        print("\n🔄 ÉTAPE 4/4 — SMS Events...")
        SmsGenerator(db).run(
            users_query=users_query,
            campaigns=campaigns,
            services=services,
        )

        # 6. Résumé
        print("\n" + "=" * 70)
        print("✅ GÉNÉRATION TERMINÉE")
        print("=" * 70)
        print_summary(db)
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