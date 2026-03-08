from sqlalchemy.orm import Session

from app.models.services import Service
from app.seeds.config import SERVICES_DATA
from app.seeds.utils import uid
from .base import BaseGenerator


class ServicesGenerator(BaseGenerator):
    name = "services"

    def run(self, service_types: list, **kwargs) -> list:
        self.log("4 services réels...")

        type_map = {st.name: st for st in service_types}

        for s in SERVICES_DATA:
            existing = (
                self.db.query(Service)
                .filter(Service.name == s["name"])
                .first()
            )
            if not existing:
                obj = Service(
                    id=uid(),
                    name=s["name"],
                    description=s["description"],
                    service_type_id=type_map[s["type"]].id,
                    is_active=True,
                )
                self.db.add(obj)
                self.created.append(obj)
            else:
                self.created.append(existing)

        self.db.commit()
        self.log_done()
        return self.created