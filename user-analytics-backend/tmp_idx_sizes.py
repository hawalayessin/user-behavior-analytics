from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    rows = db.execute(text('''
        SELECT
          indexname,
          tablename,
          pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
        FROM pg_indexes
        JOIN pg_class ON pg_class.relname = pg_indexes.indexname
        WHERE schemaname = 'public'
          AND indexname LIKE 'idx_%'
        ORDER BY pg_relation_size(indexrelid) DESC
    ''')).fetchall()
    for r in rows:
        print(f"{r[1]}\t{r[0]}\t{r[2]}")
finally:
    db.close()
