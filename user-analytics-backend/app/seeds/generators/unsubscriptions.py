import random
import uuid
from datetime import timedelta, timezone
from sqlalchemy import text

from app.seeds.utils import print_progress
from .base import BaseGenerator


TRIAL_DAYS = 3

CHURN_REASONS_VOLUNTARY_TRIAL = [
    "USER_STOP_SMS",
    "NOT_INTERESTED",
    "WEB_CANCELLATION",
]

CHURN_REASONS_VOLUNTARY_POST = [
    "USER_STOP_SMS",
    "NOT_INTERESTED",
    "WEB_CANCELLATION",
    "TOO_EXPENSIVE",
    "CONTENT_QUALITY",
]

CHURN_REASONS_TECHNICAL = [
    "INSUFFICIENT_BALANCE",
    "BILLING_FAILURE_3X",
    "CARRIER_BLOCK",
    "PHONE_INVALID",
]


def _make_aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _unsub_datetime_for_trial(start_aware, drop_day: int):
    """Datetime aléatoire dans la tranche horaire du jour d'abandon."""
    hour_offset_min = (drop_day - 1) * 24
    hour_offset_max = drop_day * 24
    random_minutes  = random.randint(hour_offset_min * 60, hour_offset_max * 60 - 1)
    return start_aware + timedelta(minutes=random_minutes)


class UnsubscriptionsGenerator(BaseGenerator):

    name = "unsubscriptions"

    def run(self, cancelled_subscriptions: list, batch_size: int = 500, **kwargs) -> list:
        total = len(cancelled_subscriptions)
        self.log(f"{total:,} unsubscriptions à générer...".replace(",", " "))

        batch = []

        for idx, sub in enumerate(cancelled_subscriptions):

            start_aware = _make_aware(sub["subscription_start_date"])
            end_aware   = _make_aware(sub["subscription_end_date"])
            days_diff   = (end_aware - start_aware).days

            # ── Drop-off pendant l'essai (≤ 3 jours) ──────────────────────
            if days_diff <= TRIAL_DAYS:
                # ✅ days_diff EST déjà 1, 2 ou 3 selon le seed subscriptions
                # La distribution 40/35/25 est portée par subscriptions.py
                # On fait confiance directement à days_diff
                days_since   = max(days_diff, 1)
                churn_type   = "VOLUNTARY"
                churn_reason = random.choice(CHURN_REASONS_VOLUNTARY_TRIAL)
                unsub_dt     = _unsub_datetime_for_trial(start_aware, days_since)

            # ── Churn post-paiement (> 3 jours) ───────────────────────────
            else:
                days_since = days_diff
                unsub_dt   = end_aware   # ✅ pas de dépassement possible

                if random.random() < 0.65:
                    churn_type   = "VOLUNTARY"
                    churn_reason = random.choice(CHURN_REASONS_VOLUNTARY_POST)
                else:
                    churn_type   = "TECHNICAL"
                    churn_reason = random.choice(CHURN_REASONS_TECHNICAL)

            batch.append({
                "p_id":                      uuid.uuid4(),
                "p_subscription_id":         uuid.UUID(str(sub["id"])),
                "p_user_id":                 uuid.UUID(str(sub["user_id"])),
                "p_service_id":              uuid.UUID(str(sub["service_id"])),
                "p_unsubscription_datetime": unsub_dt,
                "p_churn_type":              churn_type,
                "p_churn_reason":            churn_reason,
                "p_days_since_subscription": days_since,
            })

            if len(batch) >= batch_size:
                self._bulk_insert(batch)
                batch = []

            print_progress(idx + 1, total, "unsubscriptions")

        if batch:
            self._bulk_insert(batch)

        print()
        self.log_done(total)
        return []


    def _bulk_insert(self, params: list):
        self.db.execute(text("""
            INSERT INTO unsubscriptions (
                id,
                subscription_id,
                user_id,
                service_id,
                unsubscription_datetime,
                churn_type,
                churn_reason,
                days_since_subscription
            ) VALUES (
                CAST(:p_id AS uuid),
                CAST(:p_subscription_id AS uuid),
                CAST(:p_user_id AS uuid),
                CAST(:p_service_id AS uuid),
                :p_unsubscription_datetime,
                :p_churn_type,
                :p_churn_reason,
                :p_days_since_subscription
            )
        """), params)
        self.db.commit()
