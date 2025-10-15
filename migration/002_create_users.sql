-- Migration: Create users table with client_id foreign key
-- Created: 2025-10-15
-- Description: Authentication and user management with client isolation

-- UP Migration
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    client_id UUID NOT NULL REFERENCES client_entry(client_id) ON DELETE CASCADE,
    role VARCHAR(50) CHECK (role IN ('admin', 'manager', 'staff')) DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_client_id ON users(client_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Add comments
COMMENT ON TABLE users IS 'User authentication with client_id foreign key for multi-tenant isolation';
COMMENT ON COLUMN users.client_id IS 'MANDATORY - Links user to specific client for data isolation';

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create RLS policy - users can only see users from their client
CREATE POLICY users_client_isolation ON users
    FOR ALL
    USING (client_id = current_setting('app.current_client_id')::UUID);

-- DOWN Migration (Rollback)
-- DROP POLICY IF EXISTS users_client_isolation ON users;
-- DROP INDEX IF EXISTS idx_users_role;
-- DROP INDEX IF EXISTS idx_users_email;
-- DROP INDEX IF EXISTS idx_users_client_id;
-- DROP TABLE IF EXISTS users CASCADE;
