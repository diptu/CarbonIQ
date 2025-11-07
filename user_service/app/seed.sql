-- ================================
--  Core User, Roles, Permissions
-- ================================

-- 1️⃣ Insert Users
-- ============================================================

-- Apple Parent Tenant Users
INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, is_superuser, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'admin@apple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Apple Admin', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'billing@apple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Apple Billing', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'member@apple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Apple Member', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'viewer@apple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Apple Viewer', TRUE, TRUE, FALSE, now(), now())
ON CONFLICT (email) DO NOTHING;

-- Orchard Apple Sub-Tenant Users
INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, is_superuser, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'admin@orchardapple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orchard Apple Admin', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'billing@orchardapple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orchard Apple Billing', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'member@orchardapple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orchard Apple Member', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'viewer@orchardapple.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orchard Apple Viewer', TRUE, TRUE, FALSE, now(), now())
ON CONFLICT (email) DO NOTHING;

-- Orange Parent Tenant Users
INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, is_superuser, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'admin@orrange.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orange Admin', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'billing@orrange.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orange Billing', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'member@orrange.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orange Member', TRUE, TRUE, FALSE, now(), now()),
    (gen_random_uuid(), 'viewer@orrange.com', '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK', 'Orange Viewer', TRUE, TRUE, FALSE, now(), now())
ON CONFLICT (email) DO NOTHING;

-- 2️⃣ Insert Roles
INSERT INTO roles (id, name, description)
VALUES
    (gen_random_uuid(), 'TENANT_ADMIN', 'Full access to all tenant-level management features.'),
    (gen_random_uuid(), 'BILLING_ADMIN', 'Manages billing, payments, and financial settings.'),
    (gen_random_uuid(), 'MEMBER', 'Standard member with limited operational permissions.'),
    (gen_random_uuid(), 'VIEWER', 'Read-only access to view data and reports.')
ON CONFLICT (name) DO NOTHING;

-- 3️⃣ Insert Permissions
INSERT INTO permissions (id, name, description)
VALUES
    (gen_random_uuid(), 'user.create', 'Create new users'),
    (gen_random_uuid(), 'user.read', 'View users'),
    (gen_random_uuid(), 'user.update', 'Update users'),
    (gen_random_uuid(), 'user.delete', 'Delete users'),

    (gen_random_uuid(), 'role.create', 'Create roles'),
    (gen_random_uuid(), 'role.read', 'View roles'),
    (gen_random_uuid(), 'role.update', 'Edit roles'),
    (gen_random_uuid(), 'role.delete', 'Delete roles'),

    (gen_random_uuid(), 'permission.create', 'Create new permission'),
    (gen_random_uuid(), 'permission.read', 'View permission'),
    (gen_random_uuid(), 'permission.update', 'Update permissions'),
    (gen_random_uuid(), 'permission.delete', 'Delete permissions'),

    (gen_random_uuid(), 'tenant.manage', 'Manage tenant'),
    (gen_random_uuid(), 'billing.manage', 'Manage billing')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- 4️⃣ Assign Roles to Users
-- ============================================================

-- TENANT_ADMIN role → Admin users
INSERT INTO user_roles (id, user_id, role_id)
SELECT gen_random_uuid(), u.id, r.id
FROM users u
JOIN roles r ON r.name = 'TENANT_ADMIN'
WHERE u.email IN ('admin@apple.com', 'admin@orchardapple.com', 'admin@orrange.com')
ON CONFLICT DO NOTHING;

-- BILLING_ADMIN role → Billing users
INSERT INTO user_roles (id, user_id, role_id)
SELECT gen_random_uuid(), u.id, r.id
FROM users u
JOIN roles r ON r.name = 'BILLING_ADMIN'
WHERE u.email IN ('billing@apple.com', 'billing@orchardapple.com', 'billing@orrange.com')
ON CONFLICT DO NOTHING;

-- MEMBER role → Member users
INSERT INTO user_roles (id, user_id, role_id)
SELECT gen_random_uuid(), u.id, r.id
FROM users u
JOIN roles r ON r.name = 'MEMBER'
WHERE u.email IN ('member@apple.com', 'member@orchardapple.com', 'member@orrange.com')
ON CONFLICT DO NOTHING;

-- VIEWER role → Viewer users
INSERT INTO user_roles (id, user_id, role_id)
SELECT gen_random_uuid(), u.id, r.id
FROM users u
JOIN roles r ON r.name = 'VIEWER'
WHERE u.email IN ('viewer@apple.com', 'viewer@orchardapple.com', 'viewer@orrange.com')
ON CONFLICT DO NOTHING;

-- ============================================================
-- 5️⃣ Assign Permissions to Roles
-- ============================================================

-- TENANT_ADMIN → ALL permissions
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT gen_random_uuid(), r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'TENANT_ADMIN'
ON CONFLICT DO NOTHING;

-- BILLING_ADMIN → billing.manage + user.read + permission.read
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT gen_random_uuid(), r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('billing.manage','user.read','permission.read')
WHERE r.name = 'BILLING_ADMIN'
ON CONFLICT DO NOTHING;

-- MEMBER → user.read + permission.read
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT gen_random_uuid(), r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('user.read','permission.read')
WHERE r.name = 'MEMBER'
ON CONFLICT DO NOTHING;

-- VIEWER → permission.read only
INSERT INTO role_permissions (id, role_id, permission_id)
SELECT gen_random_uuid(), r.id, p.id
FROM roles r
JOIN permissions p ON p.name = 'permission.read'
WHERE r.name = 'VIEWER'
ON CONFLICT DO NOTHING;
