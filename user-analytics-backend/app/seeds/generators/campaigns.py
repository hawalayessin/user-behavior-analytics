from datetime import datetime

from sqlalchemy.orm import Session

from app.models.campaigns import Campaign
from app.seeds.config import CAMPAIGNS_DATA
from app.seeds.utils import uid
from .base import BaseGenerator


class CampaignsGenerator(BaseGenerator):
    name = "campaigns"

    def run(self, services: list, **kwargs) -> list:
        self.log("campaigns réalistes...")

        for c in CAMPAIGNS_DATA:
            existing = (
                self.db.query(Campaign)
                .filter(Campaign.name == c["name"])
                .first()
            )
            if not existing:
                service_id = (
                    services[c["service_index"]].id
                    if c["service_index"] is not None
                    else None
                )
                obj = Campaign(
                    id=uid(),
                    name=c["name"],
                    description=c["description"],
                    service_id=service_id,
                    send_datetime=datetime.fromisoformat(c["send_datetime"]),
                    target_size=c["target_size"],
                    cost=c["cost"],
                    campaign_type=c["campaign_type"],
                    status=c["status"],
                )
                self.db.add(obj)
                self.created.append(obj)
            else:
                self.created.append(existing)

        self.db.commit()
        self.log_done()
        return self.created