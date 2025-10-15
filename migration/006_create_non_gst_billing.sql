-- Migration: Create non_gst_billing table with client_id isolation
-- Created: 2025-10-15
-- Description: Non-GST billing entries (excluded from audit reports)

-- UP Migration
CREATE TABLE IF NOT EXISTS non_gst_billing (
    bill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES client_entry(client_id) ON DELETE CASCADE,
    bill_number SERIAL,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    items JSONB NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    payment_type UUID REFERENCES payment_type(payment_type_id),
    status VARCHAR(20) CHECK (status IN ('draft', 'final', 'cancelled')) DEFAULT 'final',
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_non_gst_billing_client_id ON non_gst_billing(client_id);
CREATE INDEX IF NOT EXISTS idx_non_gst_billing_date ON non_gst_billing(created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_non_gst_billing_number ON non_gst_billing(client_id, bill_number);
CREATE INDEX IF NOT EXISTS idx_non_gst_billing_status ON non_gst_billing(client_id, status);
CREATE INDEX IF NOT EXISTS idx_non_gst_billing_customer ON non_gst_billing(client_id, customer_name);

-- Add comments
COMMENT ON TABLE non_gst_billing IS 'Non-GST billing - excluded from audit reports but visible in general billing';
COMMENT ON COLUMN non_gst_billing.client_id IS 'MANDATORY - Data isolation per client';
COMMENT ON COLUMN non_gst_billing.bill_number IS 'Sequential per client_id (not global)';
COMMENT ON COLUMN non_gst_billing.items IS 'Array of {product_id, product_name, quantity, rate, amount}';
COMMENT ON COLUMN non_gst_billing.total_amount IS 'Final amount without GST';

-- Create trigger for updated_at
CREATE TRIGGER update_non_gst_billing_updated_at
    BEFORE UPDATE ON non_gst_billing
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE non_gst_billing ENABLE ROW LEVEL SECURITY;

-- Create RLS policy
CREATE POLICY non_gst_billing_client_isolation ON non_gst_billing
    FOR ALL
    USING (client_id = current_setting('app.current_client_id')::UUID);

-- DOWN Migration (Rollback)
-- DROP POLICY IF EXISTS non_gst_billing_client_isolation ON non_gst_billing;
-- DROP TRIGGER IF EXISTS update_non_gst_billing_updated_at ON non_gst_billing;
-- DROP INDEX IF EXISTS idx_non_gst_billing_customer;
-- DROP INDEX IF EXISTS idx_non_gst_billing_status;
-- DROP INDEX IF EXISTS idx_non_gst_billing_number;
-- DROP INDEX IF EXISTS idx_non_gst_billing_date;
-- DROP INDEX IF EXISTS idx_non_gst_billing_client_id;
-- DROP TABLE IF EXISTS non_gst_billing CASCADE;
