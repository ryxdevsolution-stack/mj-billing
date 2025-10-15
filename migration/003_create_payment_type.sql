-- Migration: Create payment_type table with client_id isolation
-- Created: 2025-10-15
-- Description: Payment method configuration per client (Cash, Card, UPI, etc.)

-- UP Migration
CREATE TABLE IF NOT EXISTS payment_type (
    payment_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES client_entry(client_id) ON DELETE CASCADE,
    payment_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_payment_client_id ON payment_type(client_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_client_name ON payment_type(client_id, payment_name);

-- Add comments
COMMENT ON TABLE payment_type IS 'Payment methods per client - Cash, Card, UPI, Online, Credit, Cheque';
COMMENT ON COLUMN payment_type.client_id IS 'MANDATORY - Payment types isolated per client';

-- Enable Row Level Security
ALTER TABLE payment_type ENABLE ROW LEVEL SECURITY;

-- Create RLS policy
CREATE POLICY payment_type_client_isolation ON payment_type
    FOR ALL
    USING (client_id = current_setting('app.current_client_id')::UUID);

-- DOWN Migration (Rollback)
-- DROP POLICY IF EXISTS payment_type_client_isolation ON payment_type;
-- DROP INDEX IF EXISTS idx_payment_client_name;
-- DROP INDEX IF EXISTS idx_payment_client_id;
-- DROP TABLE IF EXISTS payment_type CASCADE;
