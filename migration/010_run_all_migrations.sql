-- Master Migration Runner
-- Created: 2025-10-15
-- Description: Run all migrations in correct order

-- Instructions:
-- Connect to your Supabase PostgreSQL database and run each file in order:
-- 1. 001_create_client_entry.sql
-- 2. 002_create_users.sql
-- 3. 003_create_payment_type.sql
-- 4. 004_create_stock_entry.sql
-- 5. 005_create_gst_billing.sql
-- 6. 006_create_non_gst_billing.sql
-- 7. 007_create_report.sql
-- 8. 008_create_audit_log.sql
-- 9. 009_create_stock_reduction_trigger.sql

-- Alternative: Run all at once (uncomment to use)
-- \i 001_create_client_entry.sql
-- \i 002_create_users.sql
-- \i 003_create_payment_type.sql
-- \i 004_create_stock_entry.sql
-- \i 005_create_gst_billing.sql
-- \i 006_create_non_gst_billing.sql
-- \i 007_create_report.sql
-- \i 008_create_audit_log.sql
-- \i 009_create_stock_reduction_trigger.sql

-- Verification Queries
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
-- SELECT * FROM client_entry LIMIT 1;

-- Summary:
-- ✅ All tables created with client_id foreign keys
-- ✅ Row Level Security enabled on all tables
-- ✅ Indexes created for performance
-- ✅ Triggers for updated_at and stock reduction
-- ✅ Comments added for documentation
