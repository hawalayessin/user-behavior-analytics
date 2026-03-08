import random
import uuid

from sqlalchemy import text

from app.seeds.config import ACTIVITY_COUNT, BATCH_SIZE
from app.seeds.utils import uid, rand_date, print_progress
from .base import BaseGenerator


ACTIVITY_TYPES = [
    "service_usage",
    "sms_received",
    "sms_clicked",
    "content_viewed",
]

ACTIVITY_WEIGHTS = [40, 30, 20, 10]


class ActivitiesGenerator(BaseGenerator):
    name = "user_activities"

    def run(self, users_query, services: list, **kwargs):

        # ✅ Inclure active + inactive + cancelled (ont tous eu une activité)
        user_rows = self.db.execute(text(
            "SELECT id::text FROM users"
        )).fetchall()

        if not user_rows:
            self.log("Aucun user trouvé.")
            return []

        user_ids    = [row[0] for row in user_rows]
        service_ids = [str(s["id"]) for s in services]

        self.log(f"{ACTIVITY_COUNT:,} activités à générer".replace(",", " "))

        batch = []
        total = ACTIVITY_COUNT

        for idx in range(total):

            activity_date = rand_date(1, 365)   # ✅ élargi à 1 an

            batch.append({
                "p_id":                uuid.uuid4(),
                "p_user_id":           uuid.UUID(random.choice(user_ids)),
                "p_service_id":        uuid.UUID(random.choice(service_ids)),
                "p_activity_datetime": activity_date,
                "p_activity_type":     random.choices(
                    ACTIVITY_TYPES,
                    weights=ACTIVITY_WEIGHTS,
                    k=1
                )[0],
                "p_session_id":        str(uid()),
            })

            if len(batch) >= BATCH_SIZE:
                self._bulk_insert(batch)
                batch = []

            print_progress(idx + 1, total, "Activities")   # ✅ à chaque itération

        if batch:
            self._bulk_insert(batch)

        print()
        self.log_done(total)
        return []

    def _bulk_insert(self, params: list):
        self.db.execute(text("""
            INSERT INTO user_activities (
                id,
                user_id,
                service_id,
                activity_datetime,
                activity_type,
                session_id
            ) VALUES (
                CAST(:p_id AS uuid),
                CAST(:p_user_id AS uuid),
                CAST(:p_service_id AS uuid),
                :p_activity_datetime,
                :p_activity_type,
                :p_session_id
            )
        """), params)
        self.db.commit()
