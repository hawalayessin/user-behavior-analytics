# app/seeds/db.py

from app.core.database import SessionLocal


def get_seed_session():
    session = SessionLocal()

    # 🔥 optimisation seeder
    session.autoflush = False
    session.expire_on_commit = False

    return session