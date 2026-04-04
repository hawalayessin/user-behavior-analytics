from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    rows = db.execute(text('''
        SELECT
          i.indexname,
          i.tablename,
          pg_size_pretty(pg_relation_size(c.oid)) AS index_size
        FROM pg_indexes i
        JOIN pg_class c ON c.relname = i.indexname
        JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = i.schemaname
        WHERE i.schemaname = 'public'
          AND i.indexname LIKE 'idx_%'
        ORDER BY pg_relation_size(c.oid) DESC
    ''')).fetchall()
    for r in rows:
        print(f"{r[1]}\t{r[0]}\t{r[2]}")
finally:
    db.close()
