from sqlalchemy import text

from app.seeds.db import get_seed_session
from app.seeds.generators.activities import ActivitiesGenerator


def main():
    print("=" * 60)
    print("USER ACTIVITIES SEED")
    print("=" * 60)

    db = get_seed_session()

    try:
        # ✅ Truncate avant re-run
        print("Nettoyage table user_activities...")
        db.execute(text("TRUNCATE TABLE user_activities RESTART IDENTITY CASCADE"))
        db.commit()
        print("  Table vidée OK")

        services = [
            {"id": row.id}
            for row in db.execute(text("SELECT id FROM services"))
        ]
        print(f"\n  {len(services)} services chargés")

        ActivitiesGenerator(db).run(
            users_query=None,
            services=services,
        )

        # ── Vérification ──────────────────────────────────────────────────
        print("\nDistribution activity_type :")
        r1 = db.execute(text("""
            SELECT activity_type, COUNT(*) AS total,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
            FROM user_activities
            GROUP BY activity_type
            ORDER BY total DESC
        """))
        for row in r1.fetchall():
            print(f"  {row[0]:<20} : {row[1]:>8}  ({row[2]}%)")

        print("\nActivités par service :")
        r2 = db.execute(text("""
            SELECT srv.name, COUNT(*) AS total
            FROM user_activities ua
            JOIN services srv ON srv.id = ua.service_id
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
