"""
seed_campaigns.py — Version FINALE
Schéma campaigns figé (10 colonnes exactes):
  id, name, description, service_id, send_datetime (NOT NULL),
  target_size, cost, campaign_type, status, created_at

Usage:
  python scripts/etl/seed_campaigns.py          # insérer + assigner
  python scripts/etl/seed_campaigns.py --clear  # vider puis recréer
  python scripts/etl/seed_campaigns.py --dry-run
"""
from __future__ import annotations
import argparse, json, logging, os, uuid
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

CAMPAIGN_NS = uuid.UUID("88888888-8888-8888-8888-888888888888")

TEMPLATES = [
    # slug, name, campaign_type, description, target_size, cost
    ("ussd-ramadan-2025",    "Ramadan USSD Promo 2025",      "PROMOTIONAL",  "Campagne SMS push Ramadan — 50% sur abonnement mensuel",        120_000, 50_000.00),
    ("ussd-back-school-25",  "Rentrée Scolaire USSD 2025",   "ACQUISITION",  "Push USSD ciblé étudiants/parents rentrée septembre 2025",       80_000, 35_000.00),
    ("ussd-eid-offer-25",    "Offre Aïd USSD 2025",          "PROMOTIONAL",  "Offre spéciale Aïd El Adha — 3 jours accès gratuit",            95_000, 40_000.00),
    ("ussd-summer-25",       "Promo Été USSD 2025",          "PROMOTIONAL",  "Campagne été — tarif réduit juillet-août 2025",                  70_000, 30_000.00),
    ("ussd-retention-q4",    "Rétention Q4 USSD 2025",       "RETENTION",    "Relance abonnés inactifs depuis 15 jours via SMS",               45_000, 25_000.00),
    ("ussd-reactivation-25", "Réactivation Inactifs USSD",   "REACTIVATION", "Ciblage désabonnés des 60 derniers jours — offre retour",        30_000, 20_000.00),
    ("web-launch-sept-25",   "Lancement Sept WEB 2025",      "ACQUISITION",  "Bannières web et push notif — nouvelle offre septembre 2025",    25_000, 15_000.00),
    ("web-promo-oct-25",     "Promo Octobre WEB 2025",       "PROMOTIONAL",  "Display octobre — réduction 30% premier mois",                   22_000, 12_000.00),
    ("web-loyalty-25",       "Fidélité WEB 2025",            "RETENTION",    "Programme fidélité — email+push abonnés 6+ mois",                18_000, 10_000.00),
    ("web-upsell-25",        "Upsell Premium WEB 2025",      "UPSELL",       "Upgrade vers offre premium — abonnés plan standard",             15_000,  8_000.00),
    ("organic-direct",       "Organique / Direct",           "ORGANIC",      "Souscriptions directes sans campagne payante",                  500_000,     0.00),
]


def log(msg: str, **kw: Any) -> None:
    logging.info(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "message": msg, **kw}, ensure_ascii=True))


def get_anchor(engine) -> datetime:
    with engine.connect() as conn:
        val = conn.execute(text("SELECT MAX(event_datetime) FROM billing_events")).scalar()
    if val is None:
        raise RuntimeError("billing_events vide — relancer ETL.")
    if hasattr(val, "tzinfo") and val.tzinfo is None:
        val = val.replace(tzinfo=timezone.utc)
    log("Anchor", anchor=str(val))
    return val


def get_services(engine) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, name FROM services WHERE is_active = TRUE ORDER BY name")
        ).fetchall()
    return [{"id": r.id, "name": (r.name or "")} for r in rows]


def build(anchor: datetime, services: list[dict[str, Any]]) -> list[dict]:
    out = []
    for i, (slug, name, ctype, desc, tsize, cost) in enumerate(TEMPLATES):
        offset = (i * 5) % 60
        dur    = 14 + (i % 4) * 7
        end    = anchor - timedelta(days=offset)
        start  = end    - timedelta(days=dur)
        send   = start  + timedelta(days=1)           # send_datetime = J+1
        channel = "USSD" if "ussd" in slug else ("WEB" if "web" in slug else "ORGANIC")
        sid     = services[i % len(services)]["id"]
        out.append({
            # ---- colonnes DB ----
            "id":            uuid.uuid5(CAMPAIGN_NS, f"campaign:{slug}"),
            "name":          name,
            "description":   desc,
            "service_id":    sid,
            "send_datetime": send,
            "target_size":   tsize,
            "cost":          cost,
            "campaign_type": ctype,
            "status":        "completed" if end < anchor else "active",
            # ---- méta (non insérées) ----
            "_slug":    slug,
            "_start":   start,
            "_end":     end,
            "_channel": channel,
        })
    return out


INSERT_SQL = text("""
    INSERT INTO campaigns
        (id, name, description, service_id,
         send_datetime, target_size, cost, campaign_type, status)
    VALUES
        (:id, :name, :description, :service_id,
         :send_datetime, :target_size, :cost, :campaign_type, :status)
    ON CONFLICT (id) DO UPDATE SET
        name          = EXCLUDED.name,
        description   = EXCLUDED.description,
        service_id    = EXCLUDED.service_id,
        send_datetime = EXCLUDED.send_datetime,
        target_size   = EXCLUDED.target_size,
        cost          = EXCLUDED.cost,
        campaign_type = EXCLUDED.campaign_type,
        status        = EXCLUDED.status
""")


def db_rows(campaigns: list[dict]) -> list[dict]:
    """Retourne seulement les clés sans préfixe _ pour l'INSERT."""
    return [{k: v for k, v in c.items() if not k.startswith("_")} for c in campaigns]


def do_insert(engine, campaigns, dry_run: bool, pre_clean: bool = True) -> int:
    rows = db_rows(campaigns)
    if dry_run:
        log("DRY RUN insert", count=len(rows), sample_send_datetime=str(rows[0]["send_datetime"]))
        return len(rows)

    if pre_clean:
        try:
            with engine.begin() as conn:
                conn.execute(text("SET LOCAL lock_timeout = '10s'"))
                conn.execute(text("SET LOCAL statement_timeout = '120s'"))

                # Force a clean refresh before insertion.
                unlinked = conn.execute(text("UPDATE subscriptions SET campaign_id = NULL WHERE campaign_id IS NOT NULL"))
                conn.execute(text("TRUNCATE TABLE campaigns"))
            log("Pre-insert clean", mode="truncate", subscriptions_unlinked=unlinked.rowcount)
        except SQLAlchemyError:
            # Fallback when ACCESS EXCLUSIVE lock for TRUNCATE is unavailable.
            with engine.begin() as conn:
                conn.execute(text("SET LOCAL lock_timeout = '10s'"))
                conn.execute(text("SET LOCAL statement_timeout = '120s'"))
                unlinked = conn.execute(text("UPDATE subscriptions SET campaign_id = NULL WHERE campaign_id IS NOT NULL"))
                deleted = conn.execute(text("DELETE FROM campaigns"))
            log(
                "Pre-insert clean fallback",
                mode="delete",
                subscriptions_unlinked=unlinked.rowcount,
                campaigns_deleted=deleted.rowcount,
            )

    with engine.begin() as conn:
        conn.execute(text("SET LOCAL lock_timeout = '10s'"))
        conn.execute(text("SET LOCAL statement_timeout = '120s'"))
        conn.execute(INSERT_SQL, rows)

    log("Campaigns upserted", count=len(rows))
    return len(rows)


ASSIGN_BATCH_SQL = text(r"""
    WITH locked_subscriptions AS (
        SELECT
            s.id,
            s.service_id,
            s.subscription_start_date
        FROM subscriptions s
        WHERE s.campaign_id IS NULL
        LIMIT :batch_size
        FOR UPDATE OF s SKIP LOCKED
    ),
    candidates AS (
        SELECT
            ls.id                     AS sub_id,
            c.id                      AS campaign_id,
            ls.subscription_start_date AS sub_start,
            c.send_datetime           AS send_dt,
            ROW_NUMBER() OVER (
                PARTITION BY ls.id
                ORDER BY ABS(EXTRACT(EPOCH FROM (ls.subscription_start_date - c.send_datetime))), c.send_datetime DESC
            ) AS rn
        FROM locked_subscriptions ls
        JOIN campaigns c ON c.service_id = ls.service_id
    )
    UPDATE subscriptions s
    SET    campaign_id = c.campaign_id
    FROM   candidates c
    WHERE  s.id = c.sub_id
      AND  c.rn = 1

""")


ASSIGN_ORGANIC_FALLBACK_BATCH_SQL = text(r"""
    WITH organic_campaign AS (
        SELECT id
        FROM campaigns
        WHERE campaign_type = 'ORGANIC'
        ORDER BY send_datetime DESC
        LIMIT 1
    ),
    locked_subscriptions AS (
        SELECT s.id
        FROM subscriptions s
        WHERE s.campaign_id IS NULL
        LIMIT :batch_size
        FOR UPDATE OF s SKIP LOCKED
    )
    UPDATE subscriptions s
    SET campaign_id = oc.id
    FROM organic_campaign oc, locked_subscriptions ls
    WHERE s.id = ls.id
""")


def do_assign(engine, dry_run: bool) -> int:
    if dry_run:
        log("DRY RUN assign skipped")
        return 0

    batch_size = 5000
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            by_service_total = 0
            fallback_total = 0

            while True:
                with engine.begin() as conn:
                    conn.execute(text("SET LOCAL lock_timeout = '10s'"))
                    conn.execute(text("SET LOCAL statement_timeout = '60s'"))
                    r = conn.execute(ASSIGN_BATCH_SQL, {"batch_size": batch_size})
                changed = r.rowcount or 0
                by_service_total += changed
                if changed == 0:
                    break

            while True:
                with engine.begin() as conn:
                    conn.execute(text("SET LOCAL lock_timeout = '10s'"))
                    conn.execute(text("SET LOCAL statement_timeout = '60s'"))
                    fallback = conn.execute(ASSIGN_ORGANIC_FALLBACK_BATCH_SQL, {"batch_size": batch_size})
                changed = fallback.rowcount or 0
                fallback_total += changed
                if changed == 0:
                    break

            total = by_service_total + fallback_total
            log(
                "Subscriptions assignées",
                by_service=by_service_total,
                organic_fallback=fallback_total,
                total=total,
                attempt=attempt,
            )
            return total
        except OperationalError as exc:
            pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)
            retriable = pgcode in {"40P01", "55P03", "57014"}  # deadlock, lock timeout, statement timeout
            if not retriable or attempt == max_attempts:
                raise
            sleep_s = attempt
            log("Assign retry", attempt=attempt, wait_seconds=sleep_s, pgcode=pgcode)
            time.sleep(sleep_s)

    return 0


def do_clear(engine) -> None:
    log("Clearing...")
    try:
        with engine.begin() as conn:
            # Avoid waiting indefinitely if another transaction keeps locks.
            conn.execute(text("SET LOCAL lock_timeout = '10s'"))
            conn.execute(text("SET LOCAL statement_timeout = '120s'"))

            # Update only linked rows to avoid a full-table rewrite.
            updated = conn.execute(text("UPDATE subscriptions SET campaign_id = NULL WHERE campaign_id IS NOT NULL"))
            deleted = conn.execute(text("DELETE FROM campaigns"))
        log("Cleared.", subscriptions_unlinked=updated.rowcount, campaigns_deleted=deleted.rowcount)
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Le clear a echoue (lock/timeout probable). Fermez les transactions ouvertes puis relancez."
        ) from exc


def summary(engine) -> None:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT c.name, c.campaign_type, c.status,
                   COUNT(s.id) AS sub_count,
                   c.send_datetime::date AS send_date
            FROM   campaigns c
            LEFT   JOIN subscriptions s ON s.campaign_id = c.id
            GROUP  BY c.id, c.name, c.campaign_type, c.status, c.send_datetime
            ORDER  BY sub_count DESC
        """)).fetchall()
        assigned = conn.execute(text("SELECT COUNT(*) FROM subscriptions WHERE campaign_id IS NOT NULL")).scalar()
        total    = conn.execute(text("SELECT COUNT(*) FROM subscriptions")).scalar()

    print("\n" + "="*78)
    print(f"  {'Nom':<40} {'Type':<14} {'Subs':>8}  Envoi")
    print("-"*78)
    for r in rows:
        print(f"  {r.name:<40} {r.campaign_type:<14} {r.sub_count:>8,}  {r.send_date}")
    print("-"*78)
    pct = round(assigned*100/total, 1) if total else 0
    print(f"  Assignées : {assigned:,} / {total:,}  ({pct}%)")
    print("="*78 + "\n")


def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--clear",   action="store_true")
    args = p.parse_args()

    url    = os.getenv("ANALYTICS_CONN", "postgresql://postgres:12345hawala@localhost:5433/analytics_db")
    engine = create_engine(url, pool_pre_ping=True)

    log("start", dry_run=args.dry_run, clear=args.clear)

    if args.clear and not args.dry_run:
        do_clear(engine)

    anchor     = get_anchor(engine)
    services   = get_services(engine)
    if not services:
        raise RuntimeError("Aucun service — relancer ETL.")

    campaigns  = build(anchor, services)
    log("Campaigns construites", count=len(campaigns),
        sample_send=str(campaigns[0]["send_datetime"]))      # ← debug visible

    inserted   = do_insert(engine, campaigns, args.dry_run, pre_clean=not args.clear)
    assigned   = do_assign(engine, args.dry_run)

    if not args.dry_run:
        summary(engine)

    log("done", inserted=inserted, assigned=assigned)


if __name__ == "__main__":
    main()
