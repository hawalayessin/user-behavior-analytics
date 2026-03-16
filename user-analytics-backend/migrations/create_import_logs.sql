-- Migration SQL: create import_logs table
-- Run manually or via your migration system

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS import_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    imported_at     TIMESTAMP DEFAULT NOW(),
    admin_id        UUID REFERENCES platform_users(id),
    file_name       VARCHAR(255),
    file_type       VARCHAR(10),  -- "csv" | "sql"
    target_table    VARCHAR(50),
    mode            VARCHAR(20),
    rows_inserted   INTEGER DEFAULT 0,
    rows_skipped    INTEGER DEFAULT 0,
    status          VARCHAR(20),
    error_details   JSONB
);

CREATE INDEX IF NOT EXISTS ix_import_logs_imported_at ON import_logs(imported_at);
CREATE INDEX IF NOT EXISTS ix_import_logs_admin_id ON import_logs(admin_id);

