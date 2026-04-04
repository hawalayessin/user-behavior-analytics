-- 1) SMS volume over time by day (30d window anchored on dataset max date)
WITH anchor AS (
  SELECT MAX(event_datetime) AS ts FROM sms_events
)
SELECT date_trunc('day', event_datetime) AS day, COUNT(*) AS sms_count
FROM sms_events, anchor
WHERE anchor.ts IS NOT NULL
  AND event_datetime >= anchor.ts - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1;

-- 2) OTP rate
WITH anchor AS (
  SELECT MAX(event_datetime) AS ts FROM sms_events
), scoped AS (
  SELECT *
  FROM sms_events, anchor
  WHERE anchor.ts IS NOT NULL
    AND event_datetime >= anchor.ts - INTERVAL '30 days'
)
SELECT
  COUNT(*) AS total_sms,
  COUNT(*) FILTER (WHERE is_otp) AS otp_sms,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE is_otp) / NULLIF(COUNT(*), 0),
    2
  ) AS otp_rate_pct
FROM scoped;

-- 3) Activation SMS rate
WITH anchor AS (
  SELECT MAX(event_datetime) AS ts FROM sms_events
), scoped AS (
  SELECT *
  FROM sms_events, anchor
  WHERE anchor.ts IS NOT NULL
    AND event_datetime >= anchor.ts - INTERVAL '30 days'
)
SELECT
  COUNT(*) AS total_sms,
  COUNT(*) FILTER (WHERE is_activation) AS activation_sms,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE is_activation) / NULLIF(COUNT(*), 0),
    2
  ) AS activation_rate_pct
FROM scoped;

-- 4) SMS by service
WITH anchor AS (
  SELECT MAX(event_datetime) AS ts FROM sms_events
)
SELECT
  se.service_id,
  COALESCE(s.name, 'unknown') AS service_name,
  COUNT(*) AS sms_count
FROM sms_events se
LEFT JOIN services s ON s.id = se.service_id
CROSS JOIN anchor
WHERE anchor.ts IS NOT NULL
  AND se.event_datetime >= anchor.ts - INTERVAL '30 days'
GROUP BY se.service_id, s.name
ORDER BY sms_count DESC;

-- 5) SMS by event_type
WITH anchor AS (
  SELECT MAX(event_datetime) AS ts FROM sms_events
)
SELECT
  event_type,
  COUNT(*) AS sms_count
FROM sms_events, anchor
WHERE anchor.ts IS NOT NULL
  AND event_datetime >= anchor.ts - INTERVAL '30 days'
GROUP BY event_type
ORDER BY sms_count DESC;

-- 6) Template usage
WITH anchor AS (
  SELECT MAX(event_datetime) AS ts FROM sms_events
)
SELECT
  template_code,
  template_name,
  COUNT(*) AS usage_count
FROM sms_events, anchor
WHERE anchor.ts IS NOT NULL
  AND event_datetime >= anchor.ts - INTERVAL '30 days'
GROUP BY template_code, template_name
ORDER BY usage_count DESC;

-- 7) Latest 20 SMS messages
SELECT
  id,
  event_datetime,
  event_type,
  template_code,
  template_name,
  service_id,
  is_otp,
  is_activation,
  message_content,
  metadata
FROM sms_events
ORDER BY event_datetime DESC
LIMIT 20;
