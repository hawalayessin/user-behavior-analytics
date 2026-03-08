from sqlalchemy import text
from app.seeds.db import get_seed_session


def main():
    print("=" * 60)
    print("SUBSCRIPTIONS SEED")
    print("=" * 60)

    db = get_seed_session()

    try:
        from app.models.users import User
        from app.seeds.generators.subscriptions import SubscriptionsGenerator

        print("Nettoyage des tables liées...")
        db.execute(text("TRUNCATE TABLE unsubscriptions  RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE billing_events   RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE subscriptions    RESTART IDENTITY CASCADE"))
        db.commit()
        print("Tables vidées OK")

        print("\nChargement users / services / campaigns...")
        users_query = db.query(User)

        services = [
            {"id": row.id}
            for row in db.execute(text("SELECT id FROM services"))
        ]
        campaigns = [
            {"id": row.id}
            for row in db.execute(text("SELECT id FROM campaigns"))
        ]
        print(f"  {len(services)} services chargés")
        print(f"  {len(campaigns)} campaigns chargées")

        subscriptions, _, _ = SubscriptionsGenerator(db).run(
            users_query=users_query,
            services=services,
            campaigns=campaigns,
        )

        print("\nSEED TERMINÉ")
        print(f"Subscriptions créées : {len(subscriptions)}")

        # ── Distribution statuts ───────────────────────────────────────────
        print("\nDistribution des statuts :")
        r1 = db.execute(text("""
            SELECT status, COUNT(*) AS total,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
            FROM subscriptions
            GROUP BY status
            ORDER BY total DESC
        """))
        for row in r1.fetchall():
            print(f"  {row[0]:<12} : {row[1]:>6}  ({row[2]}%)")

        # ── Conversion calculée depuis status + dates ──────────────────────
        print("\nAnalyse conversion trial → payant :")
        r2 = db.execute(text("""
            SELECT
                COUNT(CASE WHEN status = 'active'  THEN 1 END)  AS actifs,
                COUNT(CASE WHEN status = 'expired' THEN 1 END)  AS expires,
                COUNT(CASE WHEN status = 'trial'   THEN 1 END)  AS en_cours,
                COUNT(CASE WHEN status = 'cancelled'
                            AND (subscription_end_date - subscription_start_date)
                                > INTERVAL '3 days' THEN 1 END) AS churn_post_paiement,
                COUNT(CASE WHEN status = 'cancelled'
                            AND (subscription_end_date - subscription_start_date)
                                <= INTERVAL '3 days' THEN 1 END) AS dropoff_trial
            FROM subscriptions
        """))
        row = r2.fetchone()
        total_tries = (row.actifs or 0) + (row.expires or 0) + (row.dropoff_trial or 0)
        conv_rate   = round((row.actifs / total_tries * 100), 1) if total_tries > 0 else 0
        print(f"  Actifs (convertis)       : {row.actifs}")
        print(f"  Expirés (pas convertis)  : {row.expires}")
        print(f"  En cours (trial)         : {row.en_cours}")
        print(f"  Churn post-paiement      : {row.churn_post_paiement}")
        print(f"  Drop-off pendant trial   : {row.dropoff_trial}")
        print(f"  → Taux de conversion     : {conv_rate}%")

        # ── Durée minimale cancelled ───────────────────────────────────────
        print("\nDurée minimale abonnement cancelled :")
        r3 = db.execute(text("""
            SELECT MIN(subscription_end_date - subscription_start_date)
            FROM subscriptions WHERE status = 'cancelled'
        """))
        print(f"  MIN duration = {r3.scalar()}")

    except Exception as e:
        print("ERREUR :", str(e))
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
