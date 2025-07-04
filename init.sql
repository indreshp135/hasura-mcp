-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create entitlements table
CREATE TABLE entitlements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    resource_type VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create grants table (many-to-many relationship)
CREATE TABLE grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entitlement_id UUID NOT NULL REFERENCES entitlements(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    granted_by UUID REFERENCES users(id),
    UNIQUE(user_id, entitlement_id)
);

-- Insert dummy users
INSERT INTO users (email, name) VALUES
    ('alice@example.com', 'Alice Johnson'),
    ('bob@example.com', 'Bob Smith'),
    ('charlie@example.com', 'Charlie Brown'),
    ('diana@example.com', 'Diana Prince');

-- Insert dummy entitlements
INSERT INTO entitlements (name, description, resource_type, action) VALUES
    ('Read Documents', 'Permission to read documents', 'document', 'read'),
    ('Write Documents', 'Permission to create and edit documents', 'document', 'write'),
    ('Delete Documents', 'Permission to delete documents', 'document', 'delete'),
    ('Admin Access', 'Full administrative access', 'system', 'admin'),
    ('User Management', 'Permission to manage users', 'user', 'manage'),
    ('Report Generation', 'Permission to generate reports', 'report', 'generate');

-- Insert dummy grants
INSERT INTO grants (user_id, entitlement_id, expires_at, granted_by) VALUES
    -- Alice gets read and write access
    ((SELECT id FROM users WHERE email = 'alice@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'Read Documents'), 
     NOW() + INTERVAL '1 year', 
     (SELECT id FROM users WHERE email = 'alice@example.com')),
    
    ((SELECT id FROM users WHERE email = 'alice@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'Write Documents'), 
     NOW() + INTERVAL '1 year', 
     (SELECT id FROM users WHERE email = 'alice@example.com')),
    
    -- Bob gets admin access
    ((SELECT id FROM users WHERE email = 'bob@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'Admin Access'), 
     NOW() + INTERVAL '2 years', 
     (SELECT id FROM users WHERE email = 'bob@example.com')),
    
    ((SELECT id FROM users WHERE email = 'bob@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'User Management'), 
     NOW() + INTERVAL '2 years', 
     (SELECT id FROM users WHERE email = 'bob@example.com')),
    
    -- Charlie gets read access only
    ((SELECT id FROM users WHERE email = 'charlie@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'Read Documents'), 
     NOW() + INTERVAL '6 months', 
     (SELECT id FROM users WHERE email = 'bob@example.com')),
    
    -- Diana gets report generation access
    ((SELECT id FROM users WHERE email = 'diana@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'Report Generation'), 
     NOW() + INTERVAL '1 year', 
     (SELECT id FROM users WHERE email = 'bob@example.com')),
    
    ((SELECT id FROM users WHERE email = 'diana@example.com'), 
     (SELECT id FROM entitlements WHERE name = 'Read Documents'), 
     NOW() + INTERVAL '1 year', 
     (SELECT id FROM users WHERE email = 'bob@example.com'));

-- Create indexes for better performance
CREATE INDEX idx_grants_user_id ON grants(user_id);
CREATE INDEX idx_grants_entitlement_id ON grants(entitlement_id);
CREATE INDEX idx_grants_expires_at ON grants(expires_at);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_entitlements_resource_type ON entitlements(resource_type);
CREATE INDEX idx_entitlements_action ON entitlements(action);