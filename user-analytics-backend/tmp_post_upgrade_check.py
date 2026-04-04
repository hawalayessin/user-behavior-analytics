from app.core.database import SessionLocal
from sqlalchemy import text

names = [
'idx_subscriptions_status_service_end_partial',
'idx_subscriptions_service_end',
'idx_subscriptions_service_start_user',
'idx_billing_events_sub_success_dt',
'idx_billing_events_sub_failed_dt',
'idx_campaigns_service_send_datetime',
'idx_users_status_last_activity',
'idx_user_activities_service_user_dt',
]

db=SessionLocal()
try:
    ver = db.execute(text('SELECT version_num FROM alembic_version')).fetchall()
    print('ALEMBIC_VERSION', [r[0] for r in ver])
    rows=db.execute(text('''
      SELECT indexname, tablename
      FROM pg_indexes
      WHERE schemaname='public'
        AND indexname = ANY(:names)
      ORDER BY indexname
    '''), {'names': names}).fetchall()
    print('FOUND', len(rows))
    for r in rows:
        print(r[0], r[1])
finally:
    db.close()
