-- Migration: Create client_entry table (Master client registration)
-- Created: 2025-10-15
-- Description: Master table for client registration with logo and GST info

-- UP Migration
CREATE TABLE IF NOT EXISTS client_entry (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    logo_url VARCHAR(500),
    address TEXT,
    gst_number VARCHAR(15),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_client_email ON client_entry(email);
CREATE INDEX IF NOT EXISTS idx_client_active ON client_entry(is_active);

-- Add comments
COMMENT ON TABLE client_entry IS 'Master client registration table - ALL other tables reference this via client_id';
COMMENT ON COLUMN client_entry.client_id IS 'CORE IDENTIFIER - All tables must reference this for client isolation';
COMMENT ON COLUMN client_entry.logo_url IS 'Path to client logo in Supabase Storage';

-- DOWN Migration (Rollback)
-- DROP INDEX IF EXISTS idx_client_active;
-- DROP INDEX IF EXISTS idx_client_email;
-- DROP TABLE IF EXISTS client_entry CASCADE;
