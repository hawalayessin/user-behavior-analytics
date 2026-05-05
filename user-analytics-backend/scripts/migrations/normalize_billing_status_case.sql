-- Normaliser tous les statuts billing_events en minuscules
UPDATE billing_events
SET status = LOWER(status)
WHERE status != LOWER(status);

-- Vérifier
SELECT status, COUNT(*) FROM billing_events
GROUP BY status ORDER BY COUNT(*) DESC;

-- Normaliser subscriptions.status aussi
UPDATE subscriptions
SET status = LOWER(status)
WHERE status != LOWER(status);

SELECT status, COUNT(*) FROM subscriptions
GROUP BY status ORDER BY COUNT(*) DESC;
