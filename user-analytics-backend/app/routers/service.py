from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("")
def get_services(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT id, name, url
        FROM services
        ORDER BY name ASC
    """)).fetchall()
    return [{"id": row.id, "name": row.name, "url": row.url} for row in rows]