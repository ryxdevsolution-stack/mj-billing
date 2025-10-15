-- Migration: Create test client and user for login
-- Created: 2025-10-15
-- Description: Creates a test client and user account for testing the system

-- Create test client
INSERT INTO client_entry (
    client_id,
    client_name,
    email,
    phone,
    address,
    gst_number,
    created_at,
    is_active
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',  -- Fixed UUID for testing
    'Test Company',
    'testcompany@example.com',
    '9876543210',
    '123 Main Street, Test City',
    '29ABCDE1234F1Z5',
    NOW(),
    true
);

-- Create test user with password: password123
-- Password is hashed using bcrypt with salt rounds 12
-- Note: If password doesn't work, regenerate hash using:
-- python -c "import bcrypt; print(bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode())"
INSERT INTO users (
    user_id,
    email,
    password_hash,
    client_id,
    role,
    created_at,
    is_active
) VALUES (
    '660e8400-e29b-41d4-a716-446655440001',  -- Fixed UUID for testing
    'admin@testcompany.com',
    '$2b$12$TUWvTnlnQugaq5nPilQkC.VYeQKFG8fB.4DeHPxn0tIxXgcwAfklO',  -- password123 (updated hash)
    '550e8400-e29b-41d4-a716-446655440000',  -- Links to test client
    'admin',
    NOW(),
    true
);

-- Create some default payment types for the test client
INSERT INTO payment_type (payment_type_id, client_id, payment_name, is_active, created_at) VALUES
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Cash', true, NOW()),
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Card', true, NOW()),
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'UPI', true, NOW()),
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Online', true, NOW());

-- Create some test stock items for the test client
INSERT INTO stock_entry (
    product_id,
    client_id,
    product_name,
    category,
    quantity,
    rate,
    unit,
    low_stock_alert,
    created_at
) VALUES
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Notebook', 'Stationery', 100, 50.00, 'pcs', 10, NOW()),
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Pen', 'Stationery', 200, 10.00, 'pcs', 20, NOW()),
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Pencil', 'Stationery', 150, 5.00, 'pcs', 15, NOW()),
    (gen_random_uuid(), '550e8400-e29b-41d4-a716-446655440000', 'Eraser', 'Stationery', 80, 3.00, 'pcs', 10, NOW());

-- Verify the data was inserted
SELECT 'Test client created:' as message, client_name, email, client_id FROM client_entry WHERE email = 'testcompany@example.com';
SELECT 'Test user created:' as message, email, role, client_id FROM users WHERE email = 'admin@testcompany.com';

-- Display login credentials
SELECT '========================================' as info;
SELECT 'LOGIN CREDENTIALS FOR TESTING:' as info;
SELECT '========================================' as info;
SELECT 'Email: admin@testcompany.com' as info;
SELECT 'Password: password123' as info;
SELECT 'Client ID: 550e8400-e29b-41d4-a716-446655440000' as info;
SELECT '========================================' as info;
