import random
from datetime import timedelta

from app.models.subscriptions import Subscription
from app.models.users import User

from app.seeds.config import (
    SUBSCRIPTION_SCENARIOS,
    SUBSCRIPTION_RATIO,
    BATCH_SIZE,
)

from app.seeds.utils import (
    uid,
    rand_date,
    weighted_choice,
    print_progress,
)

from .base import BaseGenerator


class SubscriptionsGenerator(BaseGenerator):

    name = "subscriptions"

    TRIAL_DURATION_DAYS = 3
    TRIAL_CHURN_RATIO   = 0.30


    def run(self, users_query, services, campaigns, **kwargs):
        from sqlalchemy.orm import load_only

        users      = users_query.options(load_only(User.id)).all()
        total_subs = int(len(users) * SUBSCRIPTION_RATIO)

        self.log(f"{total_subs:,} subscriptions à générer".replace(",", " "))

        subscriptions_created = []
        batch                 = []

        for idx in range(total_subs):

            user     = random.choice(users)
            service  = random.choice(services)
            campaign = weighted_choice(
                campaigns + [None, None],
                [1] * len(campaigns) + [len(campaigns), len(campaigns)],
            )

            start_date = rand_date(1, 365)
            end_date   = None
            status     = "trial"

            scenario = weighted_choice(
                SUBSCRIPTION_SCENARIOS["choices"],
                SUBSCRIPTION_SCENARIOS["weights"],
            )

            if scenario == "paid_active":
                status   = "active"
                end_date = None

            elif scenario == "inactive_no_balance":
                status   = "active"
                end_date = None

            elif scenario == "trial_active":
                status   = "trial"
                end_date = None

            elif scenario == "trial_expired":
                status   = "expired"
                end_date = start_date + timedelta(days=self.TRIAL_DURATION_DAYS)

            elif scenario in ["churned_voluntary", "churned_technical"]:
                status = "cancelled"

                if random.random() < self.TRIAL_CHURN_RATIO:
                    # ✅ Distribution EXACTE J1/J2/J3 portée ici
                    drop_day = random.choices(
                        [1, 2, 3],
                        weights=[40, 35, 25],
                        k=1
                    )[0]
                    end_date = start_date + timedelta(days=drop_day)
                else:
                    # Churn post-paiement J4 → J30
                    end_date = start_date + timedelta(
                        days=random.randint(4, 30)
                    )

            batch.append(
                Subscription(
                    id=uid(),
                    user_id=user.id,
                    service_id=service["id"],
                    campaign_id=campaign["id"] if campaign else None,
                    subscription_start_date=start_date,
                    subscription_end_date=end_date,
                    status=status,
                )
            )

            if len(batch) >= BATCH_SIZE:
                self.db.bulk_save_objects(batch)
                self.db.commit()
                subscriptions_created.extend(batch)
                batch.clear()

            print_progress(idx + 1, total_subs, "Subscriptions")

        if batch:
            self.db.bulk_save_objects(batch)
            self.db.commit()
            subscriptions_created.extend(batch)

        print()
        self.log_done(len(subscriptions_created))

        return subscriptions_created, [], []
