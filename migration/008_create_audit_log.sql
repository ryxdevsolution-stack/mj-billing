-- Migration: Create audit_log table with client_id isolation
-- Created: 2025-10-15
-- Description: Complete audit trail of all actions per client

-- UP Migration
CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES client_entry(client_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action_type VARCHAR(50) CHECK (action_type IN ('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT')) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_data JSONB,
    new_data JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_audit_client_id ON audit_log(client_id);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action_type ON audit_log(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_table_name ON audit_log(client_id, table_name);

-- Add comments
COMMENT ON TABLE audit_log IS 'Complete audit trail with client isolation - tracks all CRUD operations';
COMMENT ON COLUMN audit_log.client_id IS 'MANDATORY - Audit logs isolated per client';
COMMENT ON COLUMN audit_log.old_data IS 'Previous state (for UPDATE/DELETE) in JSON format';
COMMENT ON COLUMN audit_log.new_data IS 'New state (for CREATE/UPDATE) in JSON format';

-- Enable Row Level Security
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Create RLS policy
CREATE POLICY audit_log_client_isolation ON audit_log
    FOR ALL
    USING (client_id = current_setting('app.current_client_id')::UUID);

-- DOWN Migration (Rollback)
-- DROP POLICY IF EXISTS audit_log_client_isolation ON audit_log;
-- DROP INDEX IF EXISTS idx_audit_table_name;
-- DROP INDEX IF EXISTS idx_audit_action_type;
-- DROP INDEX IF EXISTS idx_audit_timestamp;
-- DROP INDEX IF EXISTS idx_audit_user_id;
-- DROP INDEX IF EXISTS idx_audit_client_id;
-- DROP TABLE IF EXISTS audit_log CASCADE;
