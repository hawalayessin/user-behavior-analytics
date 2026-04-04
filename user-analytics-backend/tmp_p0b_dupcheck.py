from app.core.database import SessionLocal
from sqlalchemy import text

new_indexes = {
    'idx_subscriptions_status_service_end_partial',
    'idx_subscriptions_service_end',
    'idx_subscriptions_service_start_user',
    'idx_billing_events_sub_success_dt',
    'idx_billing_events_sub_failed_dt',
    'idx_campaigns_service_send_datetime',
    'idx_users_status_last_activity',
    'idx_user_activities_service_user_dt',
}

existing_from_6c = {
    'idx_billing_events_datetime_status',
    'idx_billing_events_service_datetime',
    'idx_billing_events_user_datetime',
    'idx_subscriptions_end_date',
    'idx_subscriptions_status_end_date',
    'idx_subscriptions_service_start_date',
    'idx_user_activities_service_id',
    'idx_user_activities_datetime_type',
    'idx_user_activities_service_datetime',
    'idx_cohorts_service_id',
    'idx_cohorts_service_cohort_date',
}

print('NAME_DUPLICATES_WITH_6C')
print(sorted(new_indexes.intersection(existing_from_6c)))

print('\nCURRENTLY_EXIST_IN_DB')
db = SessionLocal()
try:
    rows = db.execute(text("""
      SELECT indexname
      FROM pg_indexes
      WHERE schemaname='public'
        AND indexname = ANY(:idx)
      ORDER BY indexname
    """), {'idx': list(new_indexes)}).fetchall()
    for r in rows:
        print(r[0])
finally:
    db.close()
