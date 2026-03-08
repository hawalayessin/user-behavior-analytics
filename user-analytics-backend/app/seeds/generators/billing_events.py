import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models.billing_events import BillingEvent
from app.models.unsubscriptions import Unsubscription
from app.models.services import Service
from app.models.service_types import ServiceType

from app.seeds.config import BILLING_FAILURES, BATCH_SIZE
from app.seeds.utils import uid, weighted_choice, print_progress
from .base import BaseGenerator


def _make_aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class BillingGenerator(BaseGenerator):

    name = "billing_events"

    def run(self, subscriptions: list, **kwargs) -> list:
        self.log(f"Génération billing_events ({len(subscriptions)} subscriptions)")

        # ── Churn data ────────────────────────────────────────────────────
        rows = self.db.execute(
            select(
                Unsubscription.subscription_id,
                Unsubscription.churn_type,
            )
        ).all()
        unsubs = {sub_id: churn for sub_id, churn in rows}

        # ── Billing config par service ────────────────────────────────────
        service_rows = self.db.execute(
            select(
                Service.id,
                ServiceType.billing_frequency_days,
                ServiceType.trial_duration_days,
            ).join(ServiceType, Service.service_type_id == ServiceType.id)
        ).all()
        service_config = {
            sid: (freq, trial)
            for sid, freq, trial in service_rows
        }

        batch   = []
        created = []
        total   = len(subscriptions)
        skipped = 0

        for idx, sub in enumerate(subscriptions):

            sub_id     = sub.id
            user_id    = sub.user_id
            service_id = sub.service_id
            status     = sub.status

            # ✅ trial et expired → aucun billing (jamais payé)
            if status in ("trial", "expired"):
                skipped += 1
                print_progress(idx + 1, total, "Billing events")
                continue

            config = service_config.get(service_id)
            if not config:
                skipped += 1
                print_progress(idx + 1, total, "Billing events")
                continue

            freq_days, trial_days = config

            # ✅ Normalisation timezone
            start_date   = _make_aware(sub.subscription_start_date)
            end_date     = _make_aware(sub.subscription_end_date)
            billing_date = start_date + timedelta(days=trial_days)
            limit        = end_date or datetime.now(timezone.utc)

            # ✅ Pour cancelled en drop-off trial → pas de billing non plus
            # (end_date - start_date <= 3 jours = jamais atteint billing_date)
            if billing_date >= limit:
                skipped += 1
                print_progress(idx + 1, total, "Billing events")
                continue

            is_first = True
            scenario = self._detect_scenario(status, sub_id, unsubs)

            while billing_date < limit:
                bill_status, failure_reason = self._resolve_billing_outcome(scenario)

                batch.append(
                    BillingEvent(
                        id=uid(),
                        subscription_id=sub_id,
                        user_id=user_id,
                        service_id=service_id,
                        event_datetime=billing_date,
                        status=bill_status,
                        failure_reason=failure_reason,
                        retry_count=(
                            random.randint(0, 2) if bill_status == "FAILED" else 0
                        ),
                        is_first_charge=is_first,
                    )
                )

                is_first     = False
                billing_date += timedelta(days=freq_days)

                if len(batch) >= BATCH_SIZE:
                    self.db.bulk_save_objects(batch)
                    self.db.commit()
                    created.extend(batch)
                    batch.clear()

            print_progress(idx + 1, total, "Billing events")

        if batch:
            self.db.bulk_save_objects(batch)
            self.db.commit()
            created.extend(batch)

        print()
        self.log(f"Skippés (trial/expired/drop-off) : {skipped}")
        self.log_done(len(created))
        return created

    # ── Business logic ────────────────────────────────────────────────────

    def _detect_scenario(self, status, sub_id, unsubs):
        if status == "cancelled":
            churn_type = unsubs.get(sub_id)
            if churn_type == "TECHNICAL":
                return "churned_technical"
            return "churned_voluntary"
        return "paid_active"

    def _resolve_billing_outcome(self, scenario):
        if scenario == "inactive_no_balance":
            return "FAILED", "Solde insuffisant"

        if scenario == "churned_technical":
            bill_status    = weighted_choice(["SUCCESS", "FAILED"], [40, 60])
            failure_reason = (
                random.choice(BILLING_FAILURES) if bill_status == "FAILED" else None
            )
            return bill_status, failure_reason

        # paid_active ou churned_voluntary
        bill_status    = weighted_choice(["SUCCESS", "FAILED"], [95, 5])
        failure_reason = (
            random.choice(BILLING_FAILURES) if bill_status == "FAILED" else None
        )
        return bill_status, failure_reason
