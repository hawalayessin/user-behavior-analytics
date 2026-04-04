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
        # This step can scan large historical windows; disable timeout for the current transaction.
        db.execute(text("SET LOCAL statement_timeout = 0"))

        # ─────────────────────────────────────────────
        # ÉTAPE 0 : Diagnostic des statuts réels en DB
        # ─────────────────────────────────────────────
        print("\n🔍 ÉTAPE 0 — Diagnostic des statuts disponibles...")

        status_check = db.execute(text("""
            SELECT status, COUNT(*) as cnt
            FROM subscriptions
            GROUP BY status
            ORDER BY cnt DESC
        """)).fetchall()

        print(f"   {'Status':<20} {'Count':>10}")
        print(f"   {'-'*20} {'-'*10}")
        for row in status_check:
            print(f"   {str(row.status):<20} {row.cnt:>10}")

        # Détecter automatiquement les statuts "actifs"
        # Gère string ('active') ET integer (1) ET mixed
        all_statuses = [str(row.status) for row in status_check]
        active_statuses_str = [s for s in all_statuses
                                if s in ('active', '1', 'Active', 'ACTIVE')]

        if not active_statuses_str:
            # Fallback : prendre le statut le plus fréquent comme "actif"
            active_statuses_str = [str(status_check[0].status)] if status_check else []
            print(f"\n   ⚠️  Aucun statut 'active' trouvé.")
            print(f"   ⚠️  Fallback sur le statut dominant: '{active_statuses_str}'")

        # Construire le filtre dynamique
        placeholders = ", ".join([f"'{s}'" for s in active_statuses_str])
        # Aussi gérer le cas integer
        int_placeholders = ", ".join([s for s in active_statuses_str if s.isdigit()])

        print(f"\n   → Statuts considérés comme actifs: {active_statuses_str}")

        # ─────────────────────────────────────────────
        # ÉTAPE 1 : Vérification des données sources
        # ─────────────────────────────────────────────
        print("\n📊 ÉTAPE 1 — Vérification données sources...")

        counts = db.execute(text("""
            SELECT
                COUNT(*)                    AS total_subscriptions,
                COUNT(DISTINCT user_id)     AS unique_users,
                COUNT(DISTINCT service_id)  AS unique_services,
                MIN(subscription_start_date) AS min_date,
                MAX(subscription_start_date) AS max_date
            FROM subscriptions
        """)).fetchone()

        print(f"   ✅ Total subscriptions : {counts.total_subscriptions}")
        print(f"   ✅ Unique users         : {counts.unique_users}")
        print(f"   ✅ Unique services      : {counts.unique_services}")
        print(f"   ✅ Plage dates          : {counts.min_date} → {counts.max_date}")

        if counts.total_subscriptions == 0:
            print("\n❌ Table subscriptions vide. Relancer l'ETL principal d'abord.")
            return

        # Vérifier le type de la colonne subscription_end_date
        col_type = db.execute(text("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'subscriptions'
              AND column_name = 'subscription_end_date'
        """)).scalar()
        print(f"   ✅ Type subscription_end_date : {col_type}")

        # Choisir le cast infinity selon le type
        infinity_cast = "'infinity'::timestamp" if col_type == 'timestamp without time zone' \
                   else "'infinity'::timestamptz" if col_type == 'timestamp with time zone' \
                   else "'9999-12-31'::date"

        # ─────────────────────────────────────────────
        # ÉTAPE 2 : Calcul des cohortes
        # ─────────────────────────────────────────────
        print("\n📊 ÉTAPE 2 — Calcul des cohortes (first_subscription_date)...")

        # Utiliser TOUS les abonnements (pas seulement active) pour les cohortes
        # L'entrée en cohorte = première souscription, peu importe le statut actuel
        cohort_preview = db.execute(text("""
            WITH first_sub AS (
                SELECT DISTINCT ON (user_id, service_id)
                    user_id,
                    service_id,
                    subscription_start_date AS first_sub_date
                FROM subscriptions
                WHERE subscription_start_date IS NOT NULL
                ORDER BY user_id, service_id, subscription_start_date ASC
            )
            SELECT
                date_trunc('month', first_sub_date)::date AS cohort_date,
                service_id,
                COUNT(*)                                   AS total_users
            FROM first_sub
            GROUP BY cohort_date, service_id
            ORDER BY cohort_date DESC, total_users DESC
        """)).fetchall()

        print(f"\n   {'Cohorte':<15} {'Service ID':<40} {'Users':>8}")
        print(f"   {'-'*15} {'-'*40} {'-'*8}")
        for row in cohort_preview[:10]:  # Afficher max 10 lignes
            print(f"   {str(row.cohort_date):<15} {str(row.service_id):<40} {row.total_users:>8}")
        if len(cohort_preview) > 10:
            print(f"   ... et {len(cohort_preview) - 10} autres cohortes")

        total_cohorts = len(cohort_preview)
        print(f"\n   → {total_cohorts} cohortes détectées")

        if total_cohorts == 0:
            print("\n⚠️  Aucune cohorte calculable. Vérifier subscription_start_date.")
            return

        # ─────────────────────────────────────────────
        # ÉTAPE 3 : Calcul retention adapté aux données
        # ─────────────────────────────────────────────
        print("\n📊 ÉTAPE 3 — Calcul retention D7 / D14 / D30...")

        # Calcul de la durée disponible des données
        data_span = db.execute(text("""
            SELECT
                EXTRACT(epoch FROM (MAX(subscription_start_date)
                    - MIN(subscription_start_date))) / 86400 AS span_days
            FROM subscriptions
            WHERE subscription_start_date IS NOT NULL
        """)).scalar() or 0

        print(f"\n   📅 Durée des données disponibles : ~{int(data_span)} jours")
        if data_span < 30:
            print(f"   ⚠️  Moins de 30 jours de données → D30 sera 0% ou incomplet (normal)")

        retention_preview = db.execute(text(f"""
            WITH first_sub AS (
                SELECT DISTINCT ON (user_id, service_id)
                    user_id,
                    service_id,
                    subscription_start_date AS first_sub_date
                FROM subscriptions
                WHERE subscription_start_date IS NOT NULL
                ORDER BY user_id, service_id, subscription_start_date ASC
            ),
            cohort_base AS (
                SELECT
                    date_trunc('month', first_sub_date)::date AS cohort_date,
                    service_id,
                    COUNT(*) AS total_users
                FROM first_sub
                GROUP BY cohort_date, service_id
            ),
            retention_calc AS (
                SELECT
                    date_trunc('month', fp.first_sub_date)::date AS cohort_date,
                    fp.service_id,

                    -- D7: toujours abonné 7 jours après sa première sub
                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date
                              <= fp.first_sub_date + INTERVAL '7 days'
                          AND COALESCE(
                                s2.subscription_end_date::timestamp,
                                {infinity_cast}
                              ) >= fp.first_sub_date + INTERVAL '7 days'
                    )) AS active_d7,

                    -- D14
                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date
                              <= fp.first_sub_date + INTERVAL '14 days'
                          AND COALESCE(
                                s2.subscription_end_date::timestamp,
                                {infinity_cast}
                              ) >= fp.first_sub_date + INTERVAL '14 days'
                    )) AS active_d14,

                    -- D30
                    COUNT(*) FILTER (WHERE EXISTS (
                        SELECT 1 FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date
                              <= fp.first_sub_date + INTERVAL '30 days'
                          AND COALESCE(
                                s2.subscription_end_date::timestamp,
                                {infinity_cast}
                              ) >= fp.first_sub_date + INTERVAL '30 days'
                    )) AS active_d30

                FROM first_sub fp
                GROUP BY cohort_date, fp.service_id
            )
            SELECT
                cb.cohort_date,
                cb.service_id,
                cb.total_users,
                ROUND(100.0 * COALESCE(rc.active_d7,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d7,
                ROUND(100.0 * COALESCE(rc.active_d14,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d14,
                ROUND(100.0 * COALESCE(rc.active_d30,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d30
            FROM cohort_base cb
            LEFT JOIN retention_calc rc
              ON rc.cohort_date = cb.cohort_date
             AND rc.service_id  = cb.service_id
            ORDER BY cb.cohort_date DESC
        """)).fetchall()

        print(f"\n   {'Cohorte':<12} {'D7':>8} {'D14':>8} {'D30':>8} {'Users':>8}")
        print(f"   {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for row in retention_preview[:15]:
            d7  = float(row.retention_d7)
            d14 = float(row.retention_d14)
            d30 = float(row.retention_d30)
            d7_icon  = "🟢" if d7  >= 40 else "🟡" if d7  >= 20 else "🔴"
            d30_icon = "🟢" if d30 >= 20 else "🟡" if d30 >= 10 else "🔴"
            print(
                f"   {str(row.cohort_date):<12}"
                f"  {d7_icon}{d7:>5}%"
                f"   {d14:>5}%"
                f"   {d30_icon}{d30:>5}%"
                f"   {row.total_users:>6}"
            )

        # ─────────────────────────────────────────────
        # ÉTAPE 4 : INSERT / UPDATE cohorts
        # ─────────────────────────────────────────────
        print("\n💾 ÉTAPE 4 — Insertion dans la table cohorts...")

        db.execute(text(f"""
        WITH first_sub AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_sub_date
            FROM subscriptions
            WHERE subscription_start_date IS NOT NULL
            ORDER BY user_id, service_id, subscription_start_date ASC
        ),
        cohort_base AS (
            SELECT
                date_trunc('month', first_sub_date)::date AS cohort_date,
                service_id,
                COUNT(*) AS total_users
            FROM first_sub
            GROUP BY cohort_date, service_id
        ),
        retention_calc AS (
            SELECT
                date_trunc('month', fp.first_sub_date)::date AS cohort_date,
                fp.service_id,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                      AND s2.service_id = fp.service_id
                      AND s2.subscription_start_date
                          <= fp.first_sub_date + INTERVAL '7 days'
                      AND COALESCE(s2.subscription_end_date::timestamp,
                                   {infinity_cast})
                          >= fp.first_sub_date + INTERVAL '7 days'
                )) AS active_d7,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                      AND s2.service_id = fp.service_id
                      AND s2.subscription_start_date
                          <= fp.first_sub_date + INTERVAL '14 days'
                      AND COALESCE(s2.subscription_end_date::timestamp,
                                   {infinity_cast})
                          >= fp.first_sub_date + INTERVAL '14 days'
                )) AS active_d14,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM subscriptions s2
                    WHERE s2.user_id = fp.user_id
                      AND s2.service_id = fp.service_id
                      AND s2.subscription_start_date
                          <= fp.first_sub_date + INTERVAL '30 days'
                      AND COALESCE(s2.subscription_end_date::timestamp,
                                   {infinity_cast})
                          >= fp.first_sub_date + INTERVAL '30 days'
                )) AS active_d30
            FROM first_sub fp
            GROUP BY cohort_date, fp.service_id
        ),
        retention_rates AS (
            SELECT
                cb.cohort_date,
                cb.service_id,
                cb.total_users,
                ROUND(100.0 * COALESCE(rc.active_d7,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d7,
                ROUND(100.0 * COALESCE(rc.active_d14,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d14,
                ROUND(100.0 * COALESCE(rc.active_d30,0)
                    / NULLIF(cb.total_users,0), 2) AS retention_d30
            FROM cohort_base cb
            LEFT JOIN retention_calc rc
              ON rc.cohort_date = cb.cohort_date
             AND rc.service_id  = cb.service_id
        )
        INSERT INTO cohorts (
            id, cohort_date, service_id,
            total_users, retention_d7, retention_d14, retention_d30,
            calculated_at
        )
        SELECT
            gen_random_uuid(),
            cohort_date, service_id,
            total_users, retention_d7, retention_d14, retention_d30,
            NOW()
        FROM retention_rates
        ON CONFLICT (cohort_date, service_id)
        DO UPDATE SET
            total_users    = EXCLUDED.total_users,
            retention_d7   = EXCLUDED.retention_d7,
            retention_d14  = EXCLUDED.retention_d14,
            retention_d30  = EXCLUDED.retention_d30,
            calculated_at  = NOW()
        """))

        db.commit()

        # ─────────────────────────────────────────────
        # ÉTAPE 5 : Vérification finale
        # ─────────────────────────────────────────────
        final = db.execute(text("SELECT COUNT(*) FROM cohorts")).scalar()
        sample = db.execute(text("""
            SELECT cohort_date, service_id, total_users,
                   retention_d7, retention_d14, retention_d30
            FROM cohorts
            ORDER BY cohort_date DESC
            LIMIT 3
        """)).fetchall()

        print(f"\n   ✅ {final} cohortes présentes dans la table cohorts")
        print(f"\n   Échantillon des dernières cohortes insérées:")
        for row in sample:
            print(f"   {row.cohort_date} | users={row.total_users}"
                  f" | D7={row.retention_d7}%"
                  f" | D14={row.retention_d14}%"
                  f" | D30={row.retention_d30}%")

        print("\n" + "=" * 60)
        print("✅ ETL terminé avec succès !")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()  # Stack trace complet pour debug
        raise

    finally:
        db.close()


if __name__ == "__main__":
    compute_cohorts()