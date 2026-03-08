from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


# 1️⃣ Engine = connexion PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False  # affiche requêtes SQL dans terminal
)

# 2️⃣ Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3️⃣ Base ORM
Base = declarative_base()


# 4️⃣ Dependency FastAPI (IMPORTANT)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
