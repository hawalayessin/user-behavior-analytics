-- Run these on Hawala source DB (not analytics_db)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_events_created_at
ON message_events (created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_events_event_id_created_at
ON message_events (event_id, created_at);

-- Optional compatibility index for environments where event_type_id exists on message_events
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_events_event_type_id_created_at
ON message_events (event_type_id, created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_templates_created_at
ON message_templates (created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_templates_service_id_created_at
ON message_templates (service_id, created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_templates_event_type_id_created_at
ON message_templates (event_type_id, created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_templates_event_type_id
ON message_templates (event_type_id);
