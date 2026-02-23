-- Migration 1: Unified Status Architecture
-- Adds category and is_default columns to status tables
-- Adds task statuses to the system_request_statuses table

-- 1. Add new columns to system_request_statuses
ALTER TABLE system_request_statuses ADD COLUMN IF NOT EXISTS category VARCHAR(10) NOT NULL DEFAULT 'request';
ALTER TABLE system_request_statuses ADD COLUMN IF NOT EXISTS is_default BOOLEAN NOT NULL DEFAULT false;

-- 2. Add new columns to company_request_statuses
ALTER TABLE company_request_statuses ADD COLUMN IF NOT EXISTS category VARCHAR(10) NOT NULL DEFAULT 'request';
ALTER TABLE company_request_statuses ADD COLUMN IF NOT EXISTS is_default BOOLEAN NOT NULL DEFAULT false;

-- 3. Categorize existing system statuses
-- Statuses shared by both requests and tasks
UPDATE system_request_statuses SET category = 'both' WHERE status_key IN ('pending', 'in_progress', 'review', 'completed', 'cancelled');
-- Statuses only for requests
UPDATE system_request_statuses SET category = 'request' WHERE status_key IN ('assigned', 'query_raised');
-- Set default status
UPDATE system_request_statuses SET is_default = true WHERE status_key = 'pending';

-- 4. Propagate to existing company statuses
UPDATE company_request_statuses SET category = 'both' WHERE status_key IN ('pending', 'in_progress', 'review', 'completed', 'cancelled');
UPDATE company_request_statuses SET category = 'request' WHERE status_key NOT IN ('pending', 'in_progress', 'review', 'completed', 'cancelled');
UPDATE company_request_statuses SET is_default = true WHERE status_key = 'pending';

-- 5. Migrate existing task status values to unified keys
UPDATE tasks SET status = 'pending' WHERE status = 'todo';
UPDATE tasks SET status = 'completed' WHERE status = 'done';
-- 'in_progress' and 'review' stay the same

-- 6. Create status_transitions table for workflow rules
CREATE TABLE IF NOT EXISTS status_transitions (
    id SERIAL PRIMARY KEY,
    from_status_key VARCHAR(50) NOT NULL,
    to_status_key VARCHAR(50) NOT NULL,
    allowed_roles JSON,
    requires_note BOOLEAN DEFAULT false,
    company_id VARCHAR(36) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(from_status_key, to_status_key, company_id)
);

-- 7. Seed default transition rules (NULL company_id = system defaults)
-- From pending
INSERT INTO status_transitions (from_status_key, to_status_key, allowed_roles, requires_note, company_id) VALUES
    ('pending', 'assigned', '["super_admin", "admin", "senior_accountant"]', false, NULL),
    ('pending', 'in_progress', '["super_admin", "admin", "senior_accountant", "accountant"]', false, NULL),
    ('pending', 'cancelled', '["super_admin", "admin"]', true, NULL),
    -- From assigned
    ('assigned', 'in_progress', '["super_admin", "admin", "senior_accountant", "accountant"]', false, NULL),
    ('assigned', 'pending', '["super_admin", "admin", "senior_accountant"]', false, NULL),
    ('assigned', 'cancelled', '["super_admin", "admin"]', true, NULL),
    -- From in_progress
    ('in_progress', 'review', '["super_admin", "admin", "senior_accountant", "accountant"]', false, NULL),
    ('in_progress', 'query_raised', '["super_admin", "admin", "senior_accountant", "accountant"]', false, NULL),
    ('in_progress', 'pending', '["super_admin", "admin", "senior_accountant"]', false, NULL),
    ('in_progress', 'completed', '["super_admin", "admin", "senior_accountant"]', false, NULL),
    -- From query_raised
    ('query_raised', 'in_progress', '["super_admin", "admin", "senior_accountant", "accountant"]', false, NULL),
    ('query_raised', 'pending', '["super_admin", "admin", "senior_accountant"]', false, NULL),
    -- From review
    ('review', 'completed', '["super_admin", "admin", "senior_accountant"]', false, NULL),
    ('review', 'in_progress', '["super_admin", "admin", "senior_accountant", "accountant"]', false, NULL),
    -- From completed (reopen)
    ('completed', 'in_progress', '["super_admin", "admin"]', true, NULL),
    -- From cancelled (reopen)
    ('cancelled', 'pending', '["super_admin", "admin"]', true, NULL)
ON CONFLICT (from_status_key, to_status_key, company_id) DO NOTHING;
