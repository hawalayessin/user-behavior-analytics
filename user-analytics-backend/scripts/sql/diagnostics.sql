-- Verification queries for services mapping consistency
-- Source: hawala
-- Target: analytics_db

-- 1) Source distribution by real service mapping (service_subscription_type_id -> service_id)
SELECT
    s.id AS source_service_id,
    s.entitled AS source_service_name,
    COUNT(*) AS source_subscriptions
FROM subscribed_clients sc
JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
JOIN services s ON s.id = sst.service_id
GROUP BY s.id, s.entitled
ORDER BY source_subscriptions DESC;

-- 2) Target distribution by service after fix
SELECT
    sv.id AS target_service_id,
    sv.name AS target_service_name,
    COUNT(*) AS analytics_subscriptions
FROM subscriptions sub
JOIN services sv ON sv.id = sub.service_id
GROUP BY sv.id, sv.name
ORDER BY analytics_subscriptions DESC;

-- 3) Side-by-side source vs target counts by normalized service name
WITH src AS (
    SELECT
        s.id AS source_service_id,
        s.entitled AS service_name,
        COUNT(*) AS source_count
    FROM subscribed_clients sc
    JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
    JOIN services s ON s.id = sst.service_id
    GROUP BY s.id, s.entitled
),
tgt AS (
    SELECT
        sv.id AS target_service_uuid,
        sv.name AS service_name,
        COUNT(*) AS target_count
    FROM subscriptions sub
    JOIN services sv ON sv.id = sub.service_id
    GROUP BY sv.id, sv.name
)
SELECT
    src.source_service_id,
    src.service_name,
    src.source_count,
    COALESCE(tgt.target_count, 0) AS target_count,
    src.source_count - COALESCE(tgt.target_count, 0) AS delta
FROM src
LEFT JOIN tgt ON lower(trim(tgt.service_name)) = lower(trim(src.service_name))
ORDER BY ABS(src.source_count - COALESCE(tgt.target_count, 0)) DESC, src.source_count DESC;

-- 4) Check unmapped service_subscription_type_id in source
SELECT
    sc.service_subscription_type_id,
    COUNT(*) AS rows_count
FROM subscribed_clients sc
LEFT JOIN service_subscription_types sst ON sst.id = sc.service_subscription_type_id
WHERE sc.service_subscription_type_id IS NOT NULL
  AND sst.id IS NULL
GROUP BY sc.service_subscription_type_id
ORDER BY rows_count DESC;

-- 5) Check subscriptions linked to missing users/services in analytics (should be 0)
SELECT
    SUM(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END) AS missing_users,
    SUM(CASE WHEN sv.id IS NULL THEN 1 ELSE 0 END) AS missing_services
FROM subscriptions sub
LEFT JOIN users u ON u.id = sub.user_id
LEFT JOIN services sv ON sv.id = sub.service_id;
