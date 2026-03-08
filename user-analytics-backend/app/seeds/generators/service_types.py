from sqlalchemy.orm import Session

from app.models.service_types import ServiceType
from app.seeds.config import SERVICE_TYPES_DATA
from app.seeds.utils import uid
from .base import BaseGenerator


class ServiceTypesGenerator(BaseGenerator):
    name = "service_types"

    def run(self, **kwargs) -> list:
        self.log("daily & weekly...")

        for t in SERVICE_TYPES_DATA:
            existing = (
                self.db.query(ServiceType)
                .filter(ServiceType.name == t["name"])
                .first()
            )
            if not existing:
                obj = ServiceType(id=uid(), **t, is_active=True)
                self.db.add(obj)
                self.created.append(obj)
            else:
                self.created.append(existing)

        self.db.commit()
        self.log_done()
        return self.created