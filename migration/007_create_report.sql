-- Migration: Create report table with client_id isolation
-- Created: 2025-10-15
-- Description: Auto-generated summary reports per client

-- UP Migration
CREATE TABLE IF NOT EXISTS report (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES client_entry(client_id) ON DELETE CASCADE,
    report_type VARCHAR(50) CHECK (report_type IN ('daily', 'weekly', 'monthly', 'yearly', 'custom')) NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    total_gst_bills INTEGER DEFAULT 0,
    total_non_gst_bills INTEGER DEFAULT 0,
    total_gst_amount DECIMAL(12, 2) DEFAULT 0,
    total_non_gst_amount DECIMAL(12, 2) DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    payment_breakdown JSONB,
    file_url VARCHAR(500),
    generated_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_report_client_id ON report(client_id);
CREATE INDEX IF NOT EXISTS idx_report_date_range ON report(client_id, date_from, date_to);
CREATE INDEX IF NOT EXISTS idx_report_type ON report(client_id, report_type);
CREATE INDEX IF NOT EXISTS idx_report_created ON report(created_at);

-- Add comments
COMMENT ON TABLE report IS 'Auto-generated summary reports combining GST + Non-GST data per client';
COMMENT ON COLUMN report.client_id IS 'MANDATORY - Reports isolated per client';
COMMENT ON COLUMN report.total_revenue IS 'Calculated: total_gst_amount + total_non_gst_amount';
COMMENT ON COLUMN report.payment_breakdown IS 'JSON: {Cash: 5000, UPI: 3000, Card: 2000}';
COMMENT ON COLUMN report.file_url IS 'Export path (CSV/PDF) in Supabase Storage';

-- Enable Row Level Security
ALTER TABLE report ENABLE ROW LEVEL SECURITY;

-- Create RLS policy
CREATE POLICY report_client_isolation ON report
    FOR ALL
    USING (client_id = current_setting('app.current_client_id')::UUID);

-- DOWN Migration (Rollback)
-- DROP POLICY IF EXISTS report_client_isolation ON report;
-- DROP INDEX IF EXISTS idx_report_created;
-- DROP INDEX IF EXISTS idx_report_type;
-- DROP INDEX IF EXISTS idx_report_date_range;
-- DROP INDEX IF EXISTS idx_report_client_id;
-- DROP TABLE IF EXISTS report CASCADE;
