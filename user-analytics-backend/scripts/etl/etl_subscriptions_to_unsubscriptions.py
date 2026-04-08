#!/usr/bin/env python3
"""
ETL: analyticsdb.subscriptions (cancelled + billing_failed) → analyticsdb.unsubscriptions
Source réelle: table subscriptions avec status IN ('cancelled', 'billing_failed')
"""

import os
import logging
import argparse
from uuid import uuid4

import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ─── Config DB ───────────────────────────────────────────────────────────────
def _normalize_pg_dsn(url: str) -> str:
    dsn = (url or "").strip()
    if dsn.startswith("postgresql+psycopg2://"):
        return "postgresql://" + dsn[len("postgresql+psycopg2://") :]
    if dsn.startswith("postgres+psycopg2://"):
        return "postgres://" + dsn[len("postgres+psycopg2://") :]
    return dsn


def get_analytics_dsn() -> str:
    raw = (
        os.getenv("ANALYTICS_DATABASE_URL")
        or os.getenv("ANALYTICS_CONN")
        or "postgresql://analytics_user:analytics_pass@localhost:5432/analyticsdb"
    )
    return _normalize_pg_dsn(raw)

# ─── DDL ─────────────────────────────────────────────────────────────────────
DDL_UNSUBSCRIPTIONS = """
CREATE TABLE IF NOT EXISTS unsubscriptions (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id         UUID        UNIQUE,
    user_id                 UUID        NOT NULL,
    service_id              UUID        NOT NULL,
    unsubscription_datetime TIMESTAMPTZ,
    days_since_subscription INTEGER,
    churn_reason            VARCHAR(255),
    churn_type              VARCHAR(30),
    last_billing_event_id   UUID,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_unsub_user_id     ON unsubscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_unsub_service_id  ON unsubscriptions(service_id);
CREATE INDEX IF NOT EXISTS idx_unsub_reason      ON unsubscriptions(churn_reason);
CREATE INDEX IF NOT EXISTS idx_unsub_datetime    ON unsubscriptions(unsubscription_datetime);
CREATE INDEX IF NOT EXISTS idx_unsub_sub_id      ON unsubscriptions(subscription_id);
"""

# ─── Query source ─────────────────────────────────────────────────────────────
QUERY_SOURCE = """
SELECT
    id                      AS subscription_id,
    user_id,
    service_id,
    campaign_id,
    subscription_start_date,
    subscription_end_date,
    status,
    created_at
FROM subscriptions
WHERE status IN ('cancelled', 'billing_failed')
ORDER BY subscription_end_date ASC NULLS LAST
{limit_clause}
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────

def map_reason(status: str) -> str:
    return {
        "cancelled":      "voluntary",
        "billing_failed": "billing_failed",
    }.get(status, "unknown")

def map_churn_type(status: str) -> str:
    """
    voluntary     → churn actif (client a choisi de partir)
    billing_failed → churn passif (paiement échoué = désinscription automatique)
    """
    return {
        "cancelled":      "VOLUNTARY",
        "billing_failed": "TECHNICAL",
    }.get(status, "unknown")

def compute_days(start, end) -> int | None:
    if start and end:
        delta = end - start
        return max(0, delta.days)
    return None

def determine_unsub_datetime(row):
    """
    La date de désinscription = subscription_end_date si dispo,
    sinon subscription_start_date (cas où start == end),
    sinon created_at.
    """
    if row["subscription_end_date"]:
        return row["subscription_end_date"]
    if row["subscription_start_date"]:
        return row["subscription_start_date"]
    return row["created_at"]

# ─── ETL principal ───────────────────────────────────────────────────────────

def run_etl(limit: int | None = None, dry_run: bool = False, truncate: bool = False, batch_size: int = 5000):
    conn = psycopg2.connect(get_analytics_dsn())
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # 1. Créer la table cible si elle n'existe pas
            log.info("Création/vérification de la table unsubscriptions…")
            cur.execute(DDL_UNSUBSCRIPTIONS)
            conn.commit()

            # 2. Truncate optionnel
            if truncate and not dry_run:
                log.warning("TRUNCATE TABLE unsubscriptions…")
                cur.execute("TRUNCATE TABLE unsubscriptions;")
                conn.commit()

            # 3. Compter la source
            count_q = "SELECT COUNT(*) FROM subscriptions WHERE status IN ('cancelled', 'billing_failed')"
            if limit:
                count_q += f" LIMIT {limit}"
            cur.execute(count_q)
            total_source = cur.fetchone()[0]
            log.info(f"Lignes source à traiter : {total_source:,}")

            # 4. Lire + transformer par batch
            limit_clause = f"LIMIT {limit}" if limit else ""
            cur.execute(QUERY_SOURCE.format(limit_clause=limit_clause))

            inserted = 0
            skipped  = 0
            batch    = []

            for row in cur:
                row = dict(zip(
                    ["subscription_id","user_id","service_id","campaign_id",
                     "subscription_start_date","subscription_end_date","status","created_at"],
                    row
                ))

                unsub_dt = determine_unsub_datetime(row)
                days     = compute_days(row["subscription_start_date"], row["subscription_end_date"])
                reason   = map_reason(row["status"])
                churn    = map_churn_type(row["status"])

                batch.append((
                    str(uuid4()),
                    str(row["subscription_id"]),
                    str(row["user_id"]),
                    str(row["service_id"]),
                    unsub_dt,
                    days,
                    reason,
                    churn,
                    None,
                ))

                if len(batch) >= batch_size:
                    if not dry_run:
                        _insert_batch(conn, batch)
                    inserted += len(batch)
                    log.info(f"  {inserted:,} / {total_source:,} lignes traitées…")
                    batch = []

            # dernier batch
            if batch:
                if not dry_run:
                    _insert_batch(conn, batch)
                inserted += len(batch)

            if dry_run:
                log.info(f"[DRY-RUN] {inserted:,} lignes préparées, aucune écriture.")
                conn.rollback()
            else:
                conn.commit()
                log.info(f"✅ ETL terminé — {inserted:,} lignes insérées dans unsubscriptions.")

            # 5. Stats finales
            if not dry_run:
                with conn.cursor() as c2:
                    c2.execute("""
                        SELECT churn_reason, churn_type, COUNT(*) AS cnt
                        FROM unsubscriptions
                        GROUP BY churn_reason, churn_type
                        ORDER BY cnt DESC
                    """)
                    log.info("=== Répartition dans unsubscriptions ===")
                    for r in c2.fetchall():
                        log.info(f"  reason={r[0]!s:<20} churn_type={r[1]!s:<25} count={r[2]:,}")

    except Exception as e:
        conn.rollback()
        log.error(f"Erreur ETL: {e}")
        raise
    finally:
        conn.close()


def _insert_batch(conn, batch):
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO unsubscriptions (
                id, subscription_id, user_id, service_id,
                unsubscription_datetime, days_since_subscription,
                churn_reason, churn_type, last_billing_event_id
            ) VALUES %s
            ON CONFLICT (subscription_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                unsubscription_datetime = EXCLUDED.unsubscription_datetime,
                days_since_subscription = EXCLUDED.days_since_subscription,
                churn_reason = EXCLUDED.churn_reason,
                churn_type = EXCLUDED.churn_type,
                last_billing_event_id = EXCLUDED.last_billing_event_id
        """, batch)
    conn.commit()


# ─── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="ETL subscriptions → unsubscriptions")
    parser.add_argument("--limit",           type=int,  default=None, help="Limiter N lignes (test)")
    parser.add_argument("--dry-run",         action="store_true",     help="Simuler sans écrire")
    parser.add_argument("--truncate-target", action="store_true",     help="Vider la table avant insertion")
    parser.add_argument("--batch-size",      type=int,  default=5000, help="Taille batch (défaut: 5000)")
    args = parser.parse_args()

    run_etl(
        limit      = args.limit,
        dry_run    = args.dry_run,
        truncate   = args.truncate_target,
        batch_size = args.batch_size,
    )
