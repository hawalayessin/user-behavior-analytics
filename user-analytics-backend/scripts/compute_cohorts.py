"""
ETL Script — Compute & populate cohorts table
Run: python -m scripts.compute_cohorts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal
from datetime import datetime


def compute_cohorts():
    db = SessionLocal()

    print("=" * 60)
    print("🚀 ETL — Cohorts computation started")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:

        # ─────────────────────────────────────────────
        # ÉTAPE 1 : Vérification des données sources
        # ─────────────────────────────────────────────
        print("\n📊 ÉTAPE 1 — Vérification données sources...")

        counts = db.execute(text("""
            SELECT
                COUNT(*)                                        AS total_subscriptions,
                COUNT(*) FILTER (WHERE status = 'active')       AS active_subs,
                COUNT(*) FILTER (WHERE status = 'trial')        AS trial_subs,
                COUNT(*) FILTER (WHERE status = 'cancelled')    AS cancelled_subs,
                COUNT(DISTINCT user_id)                         AS unique_users,
                COUNT(DISTINCT service_id)                      AS unique_services
            FROM subscriptions
        """)).fetchone()

        print(f"   ✅ Total subscriptions : {counts.total_subscriptions}")
        print(f"   ✅ Active (payants)     : {counts.active_subs}")
        print(f"   ✅ Trial                : {counts.trial_subs}")
        print(f"   ✅ Cancelled            : {counts.cancelled_subs}")
        print(f"   ✅ Unique users         : {counts.unique_users}")
        print(f"   ✅ Unique services      : {counts.unique_services}")

        if counts.active_subs == 0:
            print("\n⚠️ Aucun abonnement actif trouvé. Arrêt du script.")
            return


        # ─────────────────────────────────────────────
        # ÉTAPE 2 : Calcul des cohortes
        # ─────────────────────────────────────────────
        print("\n📊 ÉTAPE 2 — Calcul des cohortes (first_paid_date)...")

        cohort_preview = db.execute(text("""
            WITH first_paid AS (
                SELECT DISTINCT ON (user_id, service_id)
                    user_id,
                    service_id,
                    subscription_start_date AS first_paid_date
                FROM subscriptions
                WHERE status = 'active'
                ORDER BY user_id, service_id, subscription_start_date ASC
            )
            SELECT
                date_trunc('month', first_paid_date)::date AS cohort_date,
                service_id,
                COUNT(*) AS total_users
            FROM first_paid
            GROUP BY cohort_date, service_id
            ORDER BY cohort_date DESC, total_users DESC
        """)).fetchall()

        print(f"\n   {'Cohorte':<15} {'Service ID':<40} {'Users':>8}")
        print(f"   {'-'*15} {'-'*40} {'-'*8}")

        for row in cohort_preview:
            print(f"   {str(row.cohort_date):<15} {str(row.service_id):<40} {row.total_users:>8}")

        total_cohorts = len(cohort_preview)
        print(f"\n   → {total_cohorts} cohortes détectées")


        # ─────────────────────────────────────────────
        # ÉTAPE 3 : Calcul retention
        # ─────────────────────────────────────────────
        print("\n📊 ÉTAPE 3 — Calcul retention D7 / D14 / D30...")

        retention_preview = db.execute(text("""
            WITH first_paid AS (
                SELECT DISTINCT ON (user_id, service_id)
                    user_id,
                    service_id,
                    subscription_start_date AS first_paid_date
                FROM subscriptions
                WHERE status = 'active'
                ORDER BY user_id, service_id, subscription_start_date ASC
            ),
            cohort_base AS (
                SELECT
                    date_trunc('month', first_paid_date)::date AS cohort_date,
                    service_id,
                    COUNT(*) AS total_users
                FROM first_paid
                GROUP BY cohort_date, service_id
            ),
            retention_calc AS (
                SELECT
                    date_trunc('month', fp.first_paid_date)::date AS cohort_date,
                    fp.service_id,

                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                        AND s2.service_id = fp.service_id
                        AND s2.status = 'active'
                        AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '7 days'
                        AND COALESCE(s2.subscription_end_date,'infinity'::timestamp)
                            >= fp.first_paid_date + INTERVAL '7 days'
                    )) AS active_d7,

                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                        AND s2.service_id = fp.service_id
                        AND s2.status = 'active'
                        AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '14 days'
                        AND COALESCE(s2.subscription_end_date,'infinity'::timestamp)
                            >= fp.first_paid_date + INTERVAL '14 days'
                    )) AS active_d14,

                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                        AND s2.service_id = fp.service_id
                        AND s2.status = 'active'
                        AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '30 days'
                        AND COALESCE(s2.subscription_end_date,'infinity'::timestamp)
                            >= fp.first_paid_date + INTERVAL '30 days'
                    )) AS active_d30

                FROM first_paid fp
                GROUP BY cohort_date, fp.service_id
            )

            SELECT
                cb.cohort_date,
                cb.service_id,
                cb.total_users,
                ROUND(100.0 * COALESCE(rc.active_d7,0) / NULLIF(cb.total_users,0),2)  AS retention_d7,
                ROUND(100.0 * COALESCE(rc.active_d14,0) / NULLIF(cb.total_users,0),2) AS retention_d14,
                ROUND(100.0 * COALESCE(rc.active_d30,0) / NULLIF(cb.total_users,0),2) AS retention_d30

            FROM cohort_base cb
            LEFT JOIN retention_calc rc
            ON rc.cohort_date = cb.cohort_date
            AND rc.service_id = cb.service_id

            ORDER BY cb.cohort_date DESC
        """)).fetchall()

        print(f"\n   {'Cohorte':<12} {'D7':>8} {'D14':>8} {'D30':>8} {'Users':>8}")
        print(f"   {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for row in retention_preview:
            d7_icon = "🟢" if row.retention_d7 >= 40 else "🔴"
            d30_icon = "🟢" if row.retention_d30 >= 20 else "🔴"

            print(
                f"   {str(row.cohort_date):<12}"
                f"{d7_icon}{float(row.retention_d7):>5}% "
                f"   {float(row.retention_d14):>5}% "
                f"   {d30_icon}{float(row.retention_d30):>5}% "
                f"   {row.total_users:>6}"
            )


        # ─────────────────────────────────────────────
        # ÉTAPE 4 : INSERT / UPDATE cohorts
        # ─────────────────────────────────────────────
        print("\n💾 ÉTAPE 4 — Insertion dans la table cohorts...")

        db.execute(text("""
        WITH first_paid AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_paid_date
            FROM subscriptions
            WHERE status = 'active'
            ORDER BY user_id, service_id, subscription_start_date ASC
        ),
        cohort_base AS (
            SELECT
                date_trunc('month', first_paid_date)::date AS cohort_date,
                service_id,
                COUNT(*) AS total_users
            FROM first_paid
            GROUP BY cohort_date, service_id
        ),
        retention_calc AS (
            SELECT
                date_trunc('month', fp.first_paid_date)::date AS cohort_date,
                fp.service_id,

                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                    AND s2.service_id = fp.service_id
                    AND s2.status = 'active'
                    AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '7 days'
                    AND COALESCE(s2.subscription_end_date,'infinity'::timestamp)
                        >= fp.first_paid_date + INTERVAL '7 days'
                )) AS active_d7,

                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                    AND s2.service_id = fp.service_id
                    AND s2.status = 'active'
                    AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '14 days'
                    AND COALESCE(s2.subscription_end_date,'infinity'::timestamp)
                        >= fp.first_paid_date + INTERVAL '14 days'
                )) AS active_d14,

                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                    AND s2.service_id = fp.service_id
                    AND s2.status = 'active'
                    AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '30 days'
                    AND COALESCE(s2.subscription_end_date,'infinity'::timestamp)
                        >= fp.first_paid_date + INTERVAL '30 days'
                )) AS active_d30

            FROM first_paid fp
            GROUP BY cohort_date, fp.service_id
        ),
        retention_rates AS (
            SELECT
                cb.cohort_date,
                cb.service_id,
                cb.total_users,
                ROUND(100.0 * COALESCE(rc.active_d7,0) / NULLIF(cb.total_users,0),2)  AS retention_d7,
                ROUND(100.0 * COALESCE(rc.active_d14,0) / NULLIF(cb.total_users,0),2) AS retention_d14,
                ROUND(100.0 * COALESCE(rc.active_d30,0) / NULLIF(cb.total_users,0),2) AS retention_d30
            FROM cohort_base cb
            LEFT JOIN retention_calc rc
              ON rc.cohort_date = cb.cohort_date
             AND rc.service_id  = cb.service_id
        )
        INSERT INTO cohorts (
            id,
            cohort_date,
            service_id,
            total_users,
            retention_d7,
            retention_d14,
            retention_d30,
            calculated_at
        )
        SELECT
            gen_random_uuid(),
            cohort_date,
            service_id,
            total_users,
            retention_d7,
            retention_d14,
            retention_d30,
            NOW()
        FROM retention_rates
        ON CONFLICT (cohort_date, service_id)
        DO UPDATE SET
            total_users = EXCLUDED.total_users,
            retention_d7 = EXCLUDED.retention_d7,
            retention_d14 = EXCLUDED.retention_d14,
            retention_d30 = EXCLUDED.retention_d30,
            calculated_at = NOW()
        """))

        db.commit()


        # ─────────────────────────────────────────────
        # ÉTAPE 5 : Vérification finale
        # ─────────────────────────────────────────────
        final = db.execute(text("SELECT COUNT(*) FROM cohorts")).scalar()

        print(f"\n   ✅ {final} cohortes présentes dans la table cohorts")

        print("\n" + "=" * 60)
        print("✅ ETL terminé avec succès !")
        print("=" * 60)


    except Exception as e:
        db.rollback()
        print(f"\n❌ ERREUR : {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    compute_cohorts()