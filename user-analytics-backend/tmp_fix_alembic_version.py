from app.core.database import SessionLocal
from sqlalchemy import text

db=SessionLocal()
try:
    before = db.execute(text('SELECT version_num FROM alembic_version')).fetchall()
    print('BEFORE', [r[0] for r in before])
    db.execute(text("UPDATE alembic_version SET version_num='6c076db13bed'"))
    db.commit()
    after = db.execute(text('SELECT version_num FROM alembic_version')).fetchall()
    print('AFTER', [r[0] for r in after])
finally:
    db.close()
