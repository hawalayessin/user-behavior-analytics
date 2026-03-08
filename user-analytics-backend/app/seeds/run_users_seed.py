"""
Runner standalone pour (re)générer uniquement les users.
Usage : python -m app.seeds.run_users_seed
"""
from sqlalchemy import text
from app.seeds.db import get_seed_session
from app.seeds.generators.users import UsersGenerator
from app.seeds.config import USER_COUNT


def truncate_users(db):
    """
    Vide toutes les tables dépendantes EN CASCADE puis recrée les users.
    ⚠️  Ceci supprime aussi subscriptions, billing, unsubscriptions, activities, sms.
    """
    print("🗑️  Truncate users CASCADE...")
    db.execute(text("""
        TRUNCATE TABLE
            sms_events,
            user_activities,
            unsubscriptions,
            billing_events,
            subscriptions,
            users
        RESTART IDENTITY CASCADE
    """))
    db.commit()
    print("   ✅ Tables vidées.")


def print_stats(db):
    total = db.execute(text("SELECT COUNT(*) FROM users")).scalar()

    print("\n📊 DISTRIBUTION users :")
    for status in ["active", "inactive"]:
        c   = db.execute(text(
            "SELECT COUNT(*) FROM users WHERE status = :s"
        ), {"s": status}).scalar()
        pct = (c / total * 100) if total > 0 else 0
        print(f"   {status:<12} → {c:>6} ({pct:>5.1f}%)")

    print(f"\n   {'TOTAL':<12} → {total:>6}")

    print("\n📊 EXEMPLES numéros générés :")
    rows = db.execute(text(
        "SELECT phone_number FROM users ORDER BY RANDOM() LIMIT 5"
    )).fetchall()
    for row in rows:
        print(f"   {row[0]}")


def main():
    print("=" * 60)
    print("👥 USERS SEED — Régénération complète")
    print("=" * 60)

    db = get_seed_session()

    try:
        # 1. Truncate
        truncate_users(db)

        # 2. Générer
        print(f"\n⚙️  Génération de {USER_COUNT:,} users...".replace(",", " "))
        UsersGenerator(db).run(count=USER_COUNT)

        # 3. Stats
        print("\n" + "=" * 60)
        print("✅ GÉNÉRATION TERMINÉE")
        print("=" * 60)
        print_stats(db)
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()