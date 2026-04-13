from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.nrr_repo import get_nrr_payload


def get_nrr(db: Session) -> dict:
    return get_nrr_payload(db)
