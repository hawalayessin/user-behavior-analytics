from app.core.database import SessionLocal
from sqlalchemy import text

db=SessionLocal()
try:
    rows=db.execute(text('SELECT version_num FROM alembic_version')).fetchall()
    print('ALEMBIC_VERSION_TABLE')
    for r in rows:
        print(r[0])
finally:
    db.close()
