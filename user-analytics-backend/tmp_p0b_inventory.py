from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print('BILLING_STATUSES')
    rows = db.execute(text("SELECT DISTINCT status FROM billing_events LIMIT 20")).fetchall()
    for r in rows:
        print(repr(r[0]))

    print('\nSUBSCRIPTION_STATUSES')
    rows = db.execute(text("SELECT DISTINCT status FROM subscriptions LIMIT 20")).fetchall()
    for r in rows:
        print(repr(r[0]))

    print('\nINDEX_LIST')
    rows = db.execute(text('''
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
    ''')).fetchall()
    for r in rows:
        print(f"{r[1]}\t{r[0]}")
finally:
    db.close()
