import random
import uuid

from sqlalchemy import text

from app.seeds.config import SMS_COUNT, BATCH_SIZE
from app.seeds.utils import uid, rand_date, print_progress
from .base import BaseGenerator


class SmsGenerator(BaseGenerator):
    name = "sms_events"

    def run(self, users_query, campaigns: list, services: list, **kwargs):

        # ✅ Raw SQL — zéro ORM, zéro lazy loading
        user_rows = self.db.execute(text(
            "SELECT id::text FROM users WHERE status = 'active'"
        )).fetchall()

        if not user_rows:
            self.log("⚠️  Aucun user actif trouvé.")
            return []

        user_ids    = [row[0] for row in user_rows]
        # ✅ services = liste de dicts → accès ["id"]
        service_ids = [str(s["id"]) for s in services]
        # ✅ campaigns = liste de dicts → accès ["id"] + None possible
        campaign_ids = [str(c["id"]) for c in campaigns] + [None]

        self.log(f"{SMS_COUNT:,} SMS events à générer".replace(",", " "))

        batch = []
        total = SMS_COUNT

        for idx in range(total):

            campaign_id = random.choice(campaign_ids)
            event_type  = random.choice(["DELIVERY_SUCCESS", "DELIVERY_FAILURE"])
            direction   = random.choice(["outbound", "inbound"])

            batch.append({
                "p_id":              uuid.uuid4(),
                "p_user_id":         uuid.UUID(random.choice(user_ids)),
                "p_campaign_id":     uuid.UUID(campaign_id) if campaign_id else None,
                "p_service_id":      uuid.UUID(random.choice(service_ids)),
                "p_event_datetime":  rand_date(1, 60),
                "p_event_type":      event_type,
                "p_direction":       direction,
                "p_message_content": "Promo SMS campaign",
                "p_delivery_status": "delivered" if event_type == "DELIVERY_SUCCESS" else "failed",
            })

            if len(batch) >= BATCH_SIZE:
                self._bulk_insert(batch)
                batch = []
                print_progress(idx + 1, total, "SMS")

        if batch:
            self._bulk_insert(batch)

        print()
        self.log_done(total)
        return []

    def _bulk_insert(self, params: list):
        self.db.execute(text("""
            INSERT INTO sms_events (
                id,
                user_id,
                campaign_id,
                service_id,
                event_datetime,
                event_type,
                direction,
                message_content,
                delivery_status
            ) VALUES (
                CAST(:p_id AS uuid),
                CAST(:p_user_id AS uuid),
                CAST(:p_campaign_id AS uuid),
                CAST(:p_service_id AS uuid),
                :p_event_datetime,
                :p_event_type,
                :p_direction,
                :p_message_content,
                :p_delivery_status
            )
        """), params)
        self.db.commit()