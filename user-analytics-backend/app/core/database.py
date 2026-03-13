import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ── Lecture depuis variable d'environnement (Docker) ─────────
# Fallback localhost pour le développement sans Docker
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:12345hawala@localhost:5433/analytics_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()