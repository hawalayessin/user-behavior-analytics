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

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "options": "-c statement_timeout=10000"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()