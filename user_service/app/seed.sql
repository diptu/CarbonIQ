-- ================================
--  Core User, Roles, Permissions
-- ================================

-- 1️⃣ Insert Admin User
INSERT INTO users (
    id,
    email,
    hashed_password,
    full_name,
    is_active,
    is_verified,
    is_superuser,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin@carboniq.com',
    '$2b$12$L.M7HdQH4lz1Fppq9wWGBupqKA44WnPePTINB1Jf6tFxRjtdi03UK',
    'Nazmul Alam',
    TRUE,
    FALSE,
    TRUE,
    now(),
    now()
)
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
    (gen_random_uuid(), 'user.create', 'Create new users in the system'),
    (gen_random_uuid(), 'user.read', 'View and list users'),
    (gen_random_uuid(), 'user.update', 'Update existing user data'),
    (gen_random_uuid(), 'user.delete', 'Remove users from the system'),

    (gen_random_uuid(), 'role.create', 'Create new roles'),
    (gen_random_uuid(), 'role.read', 'View existing roles'),
    (gen_random_uuid(), 'role.update', 'Modify role details'),
    (gen_random_uuid(), 'role.delete', 'Delete roles from the system'),

    (gen_random_uuid(), 'permission.read', 'List available permissions'),

    (gen_random_uuid(), 'tenant.manage', 'Manage tenant-level configuration'),
    (gen_random_uuid(), 'billing.manage', 'Handle billing and subscription management')
ON CONFLICT (name) DO NOTHING;


-- 4️⃣ Assign TENANT_ADMIN Role to Admin User WITH ALL PERMISSIONS
INSERT INTO user_role_permissions (id, user_id, role_id, permission_id)
SELECT
    gen_random_uuid(),
    u.id,
    r.id,
    p.id
FROM users u
CROSS JOIN roles r
CROSS JOIN permissions p
WHERE u.email = 'admin@carboniq.com'
  AND r.name = 'TENANT_ADMIN'
ON CONFLICT DO NOTHING;


-- 5️⃣ Direct extra permissions for Admin (optional, can be NULL role_id)
-- Example: direct permissions bypassing role (role_id can be NULL)
INSERT INTO user_role_permissions (id, user_id, role_id, permission_id)
VALUES
    (gen_random_uuid(),
     (SELECT id FROM users WHERE email = 'admin@carboniq.com' LIMIT 1),
     NULL,
     (SELECT id FROM permissions WHERE name = 'user.create' LIMIT 1)
    ),
    (gen_random_uuid(),
     (SELECT id FROM users WHERE email = 'admin@carboniq.com' LIMIT 1),
     NULL,
     (SELECT id FROM permissions WHERE name = 'user.read' LIMIT 1)
    )
ON CONFLICT DO NOTHING;


-- -- ========================================
-- -- Optional: Tenant Bootstrap (multi-tenant)
-- -- ========================================

-- -- Create the default tenant
-- INSERT INTO tenants (id, name, domain, schema_name, created_at, updated_at)
-- VALUES (
--     gen_random_uuid(),
--     'CarbonIQ Global',
--     'carboniq.com',
--     'tenant_carboniq',
--     now(),
--     now()
-- )
-- ON CONFLICT (domain) DO NOTHING;


-- -- Add admin user as a member of the default tenant
-- INSERT INTO tenant_memberships (id, tenant_id, user_id, role_id, created_at)
-- VALUES (
--     gen_random_uuid(),
--     (SELECT id FROM tenants WHERE domain = 'carboniq.com' LIMIT 1),
--     (SELECT id FROM users WHERE email = 'admin@carboniq.com' LIMIT 1),
--     (SELECT id FROM roles WHERE name = 'TENANT_ADMIN' LIMIT 1),
--     now()
-- )
-- ON CONFLICT DO NOTHING;
