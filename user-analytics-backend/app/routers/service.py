from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("")
def get_services(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT id, name
        FROM services
        ORDER BY name ASC
    """)).fetchall()
    return [{"id": row.id, "name": row.name} for row in rows]