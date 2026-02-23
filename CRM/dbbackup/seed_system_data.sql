-- =============================================================================
-- Pointers Consulting CRM - System Seed Data
-- =============================================================================
-- This file seeds system/template data ONLY (no company-specific data)
-- Run after schema creation to populate default services, workflows, etc.
--
-- Usage:
--   docker exec -i pointers-db psql -U pointersconsulting -d accountant_crm < seed_system_data.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- 0. CLEAN EXISTING DATA (in correct order to respect foreign keys)
-- =============================================================================
-- Disable triggers temporarily for faster deletion
SET session_replication_role = replica;

-- Delete in reverse dependency order
DELETE FROM smsf_questions;
DELETE FROM form_questions;
DELETE FROM forms WHERE company_id IS NULL;
DELETE FROM email_templates WHERE company_id IS NULL;
DELETE FROM services WHERE id <= 100;  -- System services only
DELETE FROM workflow_transitions WHERE workflow_id IN (SELECT id FROM service_workflows WHERE company_id IS NULL);
DELETE FROM workflow_steps;
DELETE FROM service_workflows WHERE company_id IS NULL;
DELETE FROM tax_types;
DELETE FROM currencies;
DELETE FROM system_request_statuses;
DELETE FROM company_request_statuses WHERE company_id = 'pointers-consulting-001';
DELETE FROM users WHERE email = 'aggarwal.adarsh98@gmail.com';
DELETE FROM companies WHERE id = 'pointers-consulting-001';
DELETE FROM roles;

-- Re-enable triggers
SET session_replication_role = DEFAULT;

-- =============================================================================
-- 1. ROLES
-- =============================================================================
INSERT INTO roles (id, name, description, permissions, created_at) VALUES
(1, 'super_admin', 'Full system access', '{"all": true}', NOW()),
(2, 'admin', 'Administrative access', '{"manage_users": true, "manage_requests": true, "view_reports": true, "manage_invoices": true}', NOW()),
(3, 'senior_accountant', 'Senior accountant with admin privileges', '{"manage_users": true, "manage_requests": true, "view_reports": true, "manage_team": true}', NOW()),
(4, 'accountant', 'Accountant access', '{"manage_assigned_requests": true, "add_notes": true}', NOW()),
(5, 'external_accountant', 'External accountant access', '{"manage_assigned_requests": true, "add_notes": true, "external": true}', NOW()),
(6, 'user', 'Client user access', '{"view_own_requests": true, "create_requests": true}', NOW());

SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));

-- =============================================================================
-- 2. COMPANY (Pointers Consulting)
-- =============================================================================
INSERT INTO companies (id, name, trading_name, email, phone, address_line1, city, state, postcode, country, plan_type, max_users, max_clients, is_active, primary_color, secondary_color, tertiary_color, logo_url, sidebar_bg_color, sidebar_text_color, sidebar_hover_bg_color, created_at, updated_at)
VALUES (
    'pointers-consulting-001',
    'Pointers Consulting',
    'Pointers Consulting Pty Ltd',
    'sam@pointersconsulting.com.au',
    '+61 426 784 982',
    'Sydney',
    'Sydney',
    'NSW',
    '2000',
    'Australia',
    'enterprise',
    100,
    10000,
    true,
    '#2D8C3C',
    '#ffffff',
    '#3BA34D',
    '/assets/pointers-logo.png',
    '#0f172a',
    '#ffffff',
    '#334155',
    NOW(),
    NOW()
);

-- =============================================================================
-- 3. ADMIN USER (aggarwal.adarsh98@gmail.com / Big@200650078296)
-- Password hash generated with bcrypt
-- =============================================================================
INSERT INTO users (id, email, password_hash, role_id, company_id, first_name, last_name, is_active, is_verified, is_first_login, two_fa_enabled, created_at, updated_at)
VALUES (
    'admin-user-001',
    'aggarwal.adarsh98@gmail.com',
    '$2b$12$TpB5nMKoAxJmpMkfPcSAmOz472rc88G.DHmvDc2pffPkl4nIqrS9u', -- Big@200650078296
    1, -- super_admin
    'pointers-consulting-001',
    'Adarsh',
    'Aggarwal',
    true,
    true,
    false,
    false,
    NOW(),
    NOW()
);

-- =============================================================================
-- 4. SYSTEM REQUEST STATUSES
-- =============================================================================
INSERT INTO system_request_statuses (id, status_key, display_name, description, color, "position", is_final, is_active, created_at) OVERRIDING SYSTEM VALUE VALUES
(1, 'pending', 'Pending', 'Request is waiting to be assigned', '#f59e0b', 1, false, true, NOW()),
(2, 'assigned', 'Assigned', 'Request has been assigned to an accountant', '#3b82f6', 2, false, true, NOW()),
(3, 'in_progress', 'In Progress', 'Work is in progress', '#8b5cf6', 3, false, true, NOW()),
(4, 'query_raised', 'Query Raised', 'Waiting for client response', '#ef4444', 4, false, true, NOW()),
(5, 'review', 'Under Review', 'Work is being reviewed', '#06b6d4', 5, false, true, NOW()),
(6, 'completed', 'Completed', 'Request has been completed', '#10b981', 6, true, true, NOW()),
(7, 'cancelled', 'Cancelled', 'Request has been cancelled', '#6b7280', 7, true, true, NOW())
;

SELECT setval('system_request_statuses_id_seq', (SELECT MAX(id) FROM system_request_statuses));

-- =============================================================================
-- 4B. COMPANY REQUEST STATUSES (Kanban Board Columns for Pointers Consulting)
-- =============================================================================
INSERT INTO company_request_statuses (id, company_id, status_key, display_name, description, color, "position", wip_limit, is_final, is_active, created_at, updated_at) OVERRIDING SYSTEM VALUE VALUES
(1, 'pointers-consulting-001', 'pending', 'Pending', 'Request received, waiting to be assigned', '#F59E0B', 1, NULL, false, true, NOW(), NOW()),
(2, 'pointers-consulting-001', 'collecting_docs', 'Collecting Documents', 'Gathering required documents from client', '#8B5CF6', 2, NULL, false, true, NOW(), NOW()),
(3, 'pointers-consulting-001', 'in_progress', 'In Progress', 'Accountant actively working on the request', '#3B82F6', 3, NULL, false, true, NOW(), NOW()),
(4, 'pointers-consulting-001', 'review', 'Under Review', 'Senior accountant reviewing the work', '#F97316', 4, NULL, false, true, NOW(), NOW()),
(5, 'pointers-consulting-001', 'awaiting_client', 'Awaiting Client', 'Sent to client for approval/signature', '#6B7280', 5, NULL, false, true, NOW(), NOW()),
(6, 'pointers-consulting-001', 'lodgement', 'Ready for Lodgement', 'Ready to submit to ATO/authority', '#14B8A6', 6, NULL, false, true, NOW(), NOW()),
(7, 'pointers-consulting-001', 'invoicing', 'Invoicing', 'Generating and sending invoice', '#EC4899', 7, NULL, false, true, NOW(), NOW()),
(8, 'pointers-consulting-001', 'completed', 'Completed', 'Request successfully completed', '#10B981', 8, NULL, true, true, NOW(), NOW()),
(9, 'pointers-consulting-001', 'on_hold', 'On Hold', 'Request temporarily paused', '#9CA3AF', 9, NULL, false, true, NOW(), NOW()),
(10, 'pointers-consulting-001', 'cancelled', 'Cancelled', 'Request was cancelled', '#EF4444', 10, NULL, true, true, NOW(), NOW());

SELECT setval('company_request_statuses_id_seq', (SELECT COALESCE(MAX(id), 0) FROM company_request_statuses));

-- =============================================================================
-- 5. CURRENCIES (21 currencies for international clients)
-- =============================================================================
INSERT INTO currencies (id, code, name, symbol, is_active, created_at) VALUES
(1, 'AUD', 'Australian Dollar', '$', true, NOW()),
(2, 'USD', 'US Dollar', '$', true, NOW()),
(3, 'GBP', 'British Pound', '£', true, NOW()),
(4, 'EUR', 'Euro', '€', true, NOW()),
(5, 'AED', 'UAE Dirham', 'د.إ', true, NOW()),
(6, 'SAR', 'Saudi Riyal', '﷼', true, NOW()),
(7, 'QAR', 'Qatari Riyal', '﷼', true, NOW()),
(8, 'KWD', 'Kuwaiti Dinar', 'د.ك', true, NOW()),
(9, 'BHD', 'Bahraini Dinar', '.د.ب', true, NOW()),
(10, 'OMR', 'Omani Rial', '﷼', true, NOW()),
(11, 'INR', 'Indian Rupee', '₹', true, NOW()),
(12, 'PKR', 'Pakistani Rupee', '₨', true, NOW()),
(13, 'NZD', 'New Zealand Dollar', '$', true, NOW()),
(14, 'CAD', 'Canadian Dollar', '$', true, NOW()),
(15, 'SGD', 'Singapore Dollar', '$', true, NOW()),
(16, 'MYR', 'Malaysian Ringgit', 'RM', true, NOW()),
(17, 'ZAR', 'South African Rand', 'R', true, NOW()),
(18, 'CHF', 'Swiss Franc', 'CHF', true, NOW()),
(19, 'JPY', 'Japanese Yen', '¥', true, NOW()),
(20, 'CNY', 'Chinese Yuan', '¥', true, NOW()),
(21, 'HKD', 'Hong Kong Dollar', 'HK$', true, NOW())
;

SELECT setval('currencies_id_seq', (SELECT MAX(id) FROM currencies));

-- =============================================================================
-- 6. TAX TYPES (Australian + International)
-- =============================================================================
INSERT INTO tax_types (id, code, name, default_rate, is_active, created_at) VALUES
(1, 'GST', 'Goods and Services Tax', 10.00, true, NOW()),
(2, 'VAT', 'Value Added Tax', 20.00, true, NOW()),
(3, 'SALES_TAX', 'Sales Tax', 8.00, true, NOW()),
(4, 'NONE', 'No Tax', 0.00, true, NOW())
;

SELECT setval('tax_types_id_seq', (SELECT MAX(id) FROM tax_types));

-- =============================================================================
-- 7. SERVICE WORKFLOWS (System defaults - company_id IS NULL)
-- =============================================================================
INSERT INTO service_workflows (id, company_id, name, description, is_default, is_active, created_at, updated_at, created_by_id) VALUES
('default-workflow', NULL, 'Default Workflow', 'Standard service request workflow', true, true, NOW(), NOW(), NULL),
('workflow-tax-agent', NULL, 'Tax Agent Workflow', 'Standard workflow for tax returns and tax-related services', false, true, NOW(), NOW(), NULL),
('workflow-bas-agent', NULL, 'BAS Agent Workflow', 'Workflow for BAS lodgements, GST, and payroll services', false, true, NOW(), NOW(), NULL),
('workflow-auditor', NULL, 'SMSF Auditor Workflow', 'Workflow for SMSF audits and compliance reviews', false, true, NOW(), NOW(), NULL),
('workflow-bookkeeper', NULL, 'Bookkeeping Workflow', 'Workflow for bookkeeping, payroll, and reconciliation services', false, true, NOW(), NOW(), NULL),
('workflow-financial-planner', NULL, 'Financial Planning Workflow', 'Workflow for financial planning, advice, and strategy services', false, true, NOW(), NOW(), NULL),
('workflow-mortgage-broker', NULL, 'Mortgage Broker Workflow', 'Workflow for loan applications and finance services', false, true, NOW(), NOW(), NULL)
;

-- =============================================================================
-- 8. WORKFLOW STEPS (for all workflows)
-- =============================================================================

-- Default Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", position_x, position_y, created_at, updated_at) VALUES
('step-pending', 'default-workflow', 'pending', 'Pending', NULL, 'gray', 'START', 1, 100, 100, NOW(), NOW()),
('step-invoice-raised', 'default-workflow', 'invoice_raised', 'Invoice Raised', NULL, 'blue', 'NORMAL', 2, 300, 100, NOW(), NOW()),
('step-assigned', 'default-workflow', 'assigned', 'Assigned', NULL, 'indigo', 'NORMAL', 3, 500, 100, NOW(), NOW()),
('step-processing', 'default-workflow', 'processing', 'Processing', NULL, 'yellow', 'NORMAL', 4, 700, 100, NOW(), NOW()),
('step-query-raised', 'default-workflow', 'query_raised', 'Query Raised', NULL, 'orange', 'QUERY', 5, 700, 250, NOW(), NOW()),
('step-review', 'default-workflow', 'accountant_review_pending', 'Under Review', NULL, 'purple', 'NORMAL', 6, 500, 250, NOW(), NOW()),
('step-completed', 'default-workflow', 'completed', 'Completed', NULL, 'green', 'END', 8, 900, 100, NOW(), NOW())
;

-- Tax Agent Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", allowed_roles, position_x, position_y, created_at, updated_at) VALUES
('tax-step-pending', 'workflow-tax-agent', 'pending', 'Pending Review', NULL, 'gray', 'START', 1, '["admin", "super_admin"]', 50, 150, NOW(), NOW()),
('tax-step-docs-requested', 'workflow-tax-agent', 'documents_requested', 'Documents Requested', NULL, 'blue', 'NORMAL', 2, '["admin", "accountant", "super_admin"]', 250, 150, NOW(), NOW()),
('tax-step-docs-received', 'workflow-tax-agent', 'documents_received', 'Documents Received', NULL, 'indigo', 'NORMAL', 3, '["admin", "accountant", "super_admin"]', 450, 150, NOW(), NOW()),
('tax-step-invoice-raised', 'workflow-tax-agent', 'invoice_raised', 'Invoice Raised', NULL, 'purple', 'NORMAL', 4, '["admin", "super_admin"]', 650, 150, NOW(), NOW()),
('tax-step-assigned', 'workflow-tax-agent', 'assigned', 'Assigned to Accountant', NULL, 'blue', 'NORMAL', 5, '["admin", "super_admin"]', 850, 150, NOW(), NOW()),
('tax-step-preparation', 'workflow-tax-agent', 'in_preparation', 'Return Preparation', NULL, 'yellow', 'NORMAL', 6, '["accountant", "admin", "super_admin"]', 1050, 150, NOW(), NOW()),
('tax-step-query', 'workflow-tax-agent', 'query_raised', 'Query Raised', NULL, 'orange', 'QUERY', 7, '["accountant", "admin", "super_admin"]', 1050, 300, NOW(), NOW()),
('tax-step-review', 'workflow-tax-agent', 'client_review', 'Client Review', NULL, 'purple', 'NORMAL', 8, '["user"]', 850, 300, NOW(), NOW()),
('tax-step-lodgement', 'workflow-tax-agent', 'ready_for_lodgement', 'Ready for Lodgement', NULL, 'indigo', 'NORMAL', 9, '["accountant", "admin", "super_admin"]', 1250, 150, NOW(), NOW()),
('tax-step-lodged', 'workflow-tax-agent', 'lodged', 'Lodged with ATO', NULL, 'blue', 'NORMAL', 10, '["accountant", "admin", "super_admin"]', 1450, 150, NOW(), NOW()),
('tax-step-admin-review', 'workflow-tax-agent', 'admin_review', 'Admin Review', NULL, 'purple', 'NORMAL', 11, '["admin", "super_admin"]', 1550, 150, NOW(), NOW()),
('tax-step-completed', 'workflow-tax-agent', 'completed', 'Completed', NULL, 'green', 'END', 12, '["accountant", "admin", "super_admin"]', 1650, 150, NOW(), NOW())
;

-- BAS Agent Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", allowed_roles, position_x, position_y, created_at, updated_at) VALUES
('bas-step-pending', 'workflow-bas-agent', 'pending', 'Pending', NULL, 'gray', 'START', 1, '["admin", "super_admin"]', 50, 150, NOW(), NOW()),
('bas-step-data-collection', 'workflow-bas-agent', 'data_collection', 'Data Collection', NULL, 'blue', 'NORMAL', 2, '["admin", "accountant", "super_admin"]', 250, 150, NOW(), NOW()),
('bas-step-invoice-raised', 'workflow-bas-agent', 'invoice_raised', 'Invoice Raised', NULL, 'purple', 'NORMAL', 3, '["admin", "super_admin"]', 450, 150, NOW(), NOW()),
('bas-step-assigned', 'workflow-bas-agent', 'assigned', 'Assigned', NULL, 'blue', 'NORMAL', 4, '["admin", "super_admin"]', 650, 150, NOW(), NOW()),
('bas-step-reconciliation', 'workflow-bas-agent', 'reconciliation', 'Bank Reconciliation', NULL, 'yellow', 'NORMAL', 5, '["accountant", "admin", "super_admin"]', 850, 150, NOW(), NOW()),
('bas-step-preparation', 'workflow-bas-agent', 'bas_preparation', 'BAS Preparation', NULL, 'yellow', 'NORMAL', 6, '["accountant", "admin", "super_admin"]', 1050, 150, NOW(), NOW()),
('bas-step-query', 'workflow-bas-agent', 'query_raised', 'Query Raised', NULL, 'orange', 'QUERY', 7, '["accountant", "admin", "super_admin"]', 1050, 300, NOW(), NOW()),
('bas-step-review', 'workflow-bas-agent', 'review', 'Review & Approval', NULL, 'purple', 'NORMAL', 8, '["admin", "super_admin"]', 1250, 150, NOW(), NOW()),
('bas-step-lodged', 'workflow-bas-agent', 'lodged', 'Lodged with ATO', NULL, 'blue', 'NORMAL', 9, '["accountant", "admin", "super_admin"]', 1450, 150, NOW(), NOW()),
('bas-step-admin-review', 'workflow-bas-agent', 'admin_review', 'Admin Final Review', NULL, 'purple', 'NORMAL', 10, '["admin", "super_admin"]', 1550, 150, NOW(), NOW()),
('bas-step-completed', 'workflow-bas-agent', 'completed', 'Completed', NULL, 'green', 'END', 11, '["accountant", "admin", "super_admin"]', 1650, 150, NOW(), NOW())
;

-- SMSF Auditor Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", allowed_roles, position_x, position_y, created_at, updated_at) VALUES
('aud-step-pending', 'workflow-auditor', 'pending', 'Audit Requested', NULL, 'gray', 'START', 1, '["admin", "super_admin"]', 50, 150, NOW(), NOW()),
('aud-step-engagement', 'workflow-auditor', 'engagement_letter', 'Engagement Letter', NULL, 'blue', 'NORMAL', 2, '["admin", "super_admin"]', 250, 150, NOW(), NOW()),
('aud-step-docs-requested', 'workflow-auditor', 'documents_requested', 'Documents Requested', NULL, 'blue', 'NORMAL', 3, '["admin", "accountant", "super_admin"]', 450, 150, NOW(), NOW()),
('aud-step-docs-received', 'workflow-auditor', 'documents_received', 'Documents Received', NULL, 'indigo', 'NORMAL', 4, '["admin", "accountant", "super_admin"]', 650, 150, NOW(), NOW()),
('aud-step-invoice-raised', 'workflow-auditor', 'invoice_raised', 'Invoice Raised', NULL, 'purple', 'NORMAL', 5, '["admin", "super_admin"]', 850, 150, NOW(), NOW()),
('aud-step-assigned', 'workflow-auditor', 'assigned', 'Assigned to Auditor', NULL, 'blue', 'NORMAL', 6, '["admin", "super_admin"]', 1050, 150, NOW(), NOW()),
('aud-step-fieldwork', 'workflow-auditor', 'fieldwork', 'Audit Fieldwork', NULL, 'yellow', 'NORMAL', 7, '["accountant", "admin", "super_admin"]', 1250, 150, NOW(), NOW()),
('aud-step-query', 'workflow-auditor', 'query_raised', 'Query Raised', NULL, 'orange', 'QUERY', 8, '["accountant", "admin", "super_admin"]', 1250, 300, NOW(), NOW()),
('aud-step-draft-report', 'workflow-auditor', 'draft_report', 'Draft Report', NULL, 'purple', 'NORMAL', 9, '["accountant", "admin", "super_admin"]', 1450, 150, NOW(), NOW()),
('aud-step-management-review', 'workflow-auditor', 'management_review', 'Management Review', NULL, 'indigo', 'NORMAL', 10, '["admin", "super_admin"]', 1650, 150, NOW(), NOW()),
('aud-step-final-report', 'workflow-auditor', 'final_report', 'Final Report Issued', NULL, 'blue', 'NORMAL', 11, '["admin", "super_admin"]', 1850, 150, NOW(), NOW()),
('aud-step-completed', 'workflow-auditor', 'completed', 'Completed', NULL, 'green', 'END', 12, '["admin", "super_admin"]', 2050, 150, NOW(), NOW())
;

-- Bookkeeper Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", allowed_roles, position_x, position_y, created_at, updated_at) VALUES
('book-step-pending', 'workflow-bookkeeper', 'pending', 'Pending', NULL, 'gray', 'START', 1, '["admin", "super_admin"]', 50, 150, NOW(), NOW()),
('book-step-access-setup', 'workflow-bookkeeper', 'access_setup', 'Access Setup', NULL, 'blue', 'NORMAL', 2, '["admin", "accountant", "super_admin"]', 250, 150, NOW(), NOW()),
('book-step-invoice-raised', 'workflow-bookkeeper', 'invoice_raised', 'Invoice Raised', NULL, 'purple', 'NORMAL', 3, '["admin", "super_admin"]', 450, 150, NOW(), NOW()),
('book-step-assigned', 'workflow-bookkeeper', 'assigned', 'Assigned', NULL, 'blue', 'NORMAL', 4, '["admin", "super_admin"]', 650, 150, NOW(), NOW()),
('book-step-processing', 'workflow-bookkeeper', 'processing', 'Processing', NULL, 'yellow', 'NORMAL', 5, '["accountant", "admin", "super_admin"]', 850, 150, NOW(), NOW()),
('book-step-query', 'workflow-bookkeeper', 'query_raised', 'Query Raised', NULL, 'orange', 'QUERY', 6, '["accountant", "admin", "super_admin"]', 850, 300, NOW(), NOW()),
('book-step-review', 'workflow-bookkeeper', 'review', 'Review', NULL, 'purple', 'NORMAL', 7, '["admin", "super_admin"]', 1050, 150, NOW(), NOW()),
('book-step-client-approval', 'workflow-bookkeeper', 'client_approval', 'Client Approval', NULL, 'indigo', 'NORMAL', 8, '["user"]', 1250, 150, NOW(), NOW()),
('book-step-admin-review', 'workflow-bookkeeper', 'admin_review', 'Admin Final Review', NULL, 'purple', 'NORMAL', 9, '["admin", "super_admin"]', 1350, 150, NOW(), NOW()),
('book-step-completed', 'workflow-bookkeeper', 'completed', 'Completed', NULL, 'green', 'END', 10, '["accountant", "admin", "super_admin"]', 1450, 150, NOW(), NOW())
;

-- Financial Planner Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", allowed_roles, position_x, position_y, created_at, updated_at) VALUES
('fp-step-pending', 'workflow-financial-planner', 'pending', 'Enquiry Received', NULL, 'gray', 'START', 1, '["admin", "super_admin"]', 50, 150, NOW(), NOW()),
('fp-step-discovery', 'workflow-financial-planner', 'discovery', 'Discovery Meeting', NULL, 'blue', 'NORMAL', 2, '["admin", "accountant", "super_admin"]', 250, 150, NOW(), NOW()),
('fp-step-fact-find', 'workflow-financial-planner', 'fact_find', 'Fact Find', NULL, 'indigo', 'NORMAL', 3, '["admin", "accountant", "super_admin"]', 450, 150, NOW(), NOW()),
('fp-step-invoice-raised', 'workflow-financial-planner', 'invoice_raised', 'Invoice Raised', NULL, 'purple', 'NORMAL', 4, '["admin", "super_admin"]', 650, 150, NOW(), NOW()),
('fp-step-assigned', 'workflow-financial-planner', 'assigned', 'Assigned to Planner', NULL, 'blue', 'NORMAL', 5, '["admin", "super_admin"]', 850, 150, NOW(), NOW()),
('fp-step-analysis', 'workflow-financial-planner', 'analysis', 'Analysis & Research', NULL, 'yellow', 'NORMAL', 6, '["accountant", "admin", "super_admin"]', 1050, 150, NOW(), NOW()),
('fp-step-soa-prep', 'workflow-financial-planner', 'soa_preparation', 'SOA Preparation', NULL, 'yellow', 'NORMAL', 7, '["accountant", "admin", "super_admin"]', 1250, 150, NOW(), NOW()),
('fp-step-compliance-review', 'workflow-financial-planner', 'compliance_review', 'Compliance Review', NULL, 'purple', 'NORMAL', 8, '["admin", "super_admin"]', 1450, 150, NOW(), NOW()),
('fp-step-presentation', 'workflow-financial-planner', 'presentation', 'Advice Presentation', NULL, 'indigo', 'NORMAL', 9, '["admin", "accountant", "super_admin"]', 1650, 150, NOW(), NOW()),
('fp-step-query', 'workflow-financial-planner', 'query_raised', 'Query Raised', NULL, 'orange', 'QUERY', 10, '["accountant", "admin", "super_admin"]', 1650, 300, NOW(), NOW()),
('fp-step-implementation', 'workflow-financial-planner', 'implementation', 'Implementation', NULL, 'blue', 'NORMAL', 11, '["accountant", "admin", "super_admin"]', 1850, 150, NOW(), NOW()),
('fp-step-admin-review', 'workflow-financial-planner', 'admin_review', 'Admin Final Review', NULL, 'purple', 'NORMAL', 12, '["admin", "super_admin"]', 1950, 150, NOW(), NOW()),
('fp-step-completed', 'workflow-financial-planner', 'completed', 'Completed', NULL, 'green', 'END', 13, '["admin", "super_admin"]', 2050, 150, NOW(), NOW())
;

-- Mortgage Broker Workflow Steps
INSERT INTO workflow_steps (id, workflow_id, name, display_name, description, color, step_type, "order", allowed_roles, position_x, position_y, created_at, updated_at) VALUES
('mb-step-pending', 'workflow-mortgage-broker', 'pending', 'Enquiry Received', NULL, 'gray', 'START', 1, '["admin", "super_admin"]', 50, 150, NOW(), NOW()),
('mb-step-consultation', 'workflow-mortgage-broker', 'consultation', 'Initial Consultation', NULL, 'blue', 'NORMAL', 2, '["admin", "accountant", "super_admin"]', 250, 150, NOW(), NOW()),
('mb-step-docs-collection', 'workflow-mortgage-broker', 'documents_collection', 'Document Collection', NULL, 'indigo', 'NORMAL', 3, '["admin", "accountant", "super_admin"]', 450, 150, NOW(), NOW()),
('mb-step-serviceability', 'workflow-mortgage-broker', 'serviceability', 'Serviceability Assessment', NULL, 'yellow', 'NORMAL', 4, '["accountant", "admin", "super_admin"]', 650, 150, NOW(), NOW()),
('mb-step-product-selection', 'workflow-mortgage-broker', 'product_selection', 'Product Selection', NULL, 'purple', 'NORMAL', 5, '["accountant", "admin", "super_admin"]', 850, 150, NOW(), NOW()),
('mb-step-invoice-raised', 'workflow-mortgage-broker', 'invoice_raised', 'Invoice Raised', NULL, 'purple', 'NORMAL', 6, '["admin", "super_admin"]', 1050, 150, NOW(), NOW()),
('mb-step-application', 'workflow-mortgage-broker', 'application_submitted', 'Application Submitted', NULL, 'blue', 'NORMAL', 7, '["accountant", "admin", "super_admin"]', 1250, 150, NOW(), NOW()),
('mb-step-assessment', 'workflow-mortgage-broker', 'lender_assessment', 'Lender Assessment', NULL, 'yellow', 'NORMAL', 8, '["accountant", "admin", "super_admin"]', 1450, 150, NOW(), NOW()),
('mb-step-query', 'workflow-mortgage-broker', 'query_raised', 'Additional Info Required', NULL, 'orange', 'QUERY', 9, '["accountant", "admin", "super_admin"]', 1450, 300, NOW(), NOW()),
('mb-step-conditional', 'workflow-mortgage-broker', 'conditional_approval', 'Conditional Approval', NULL, 'indigo', 'NORMAL', 10, '["accountant", "admin", "super_admin"]', 1650, 150, NOW(), NOW()),
('mb-step-unconditional', 'workflow-mortgage-broker', 'unconditional_approval', 'Unconditional Approval', NULL, 'blue', 'NORMAL', 11, '["accountant", "admin", "super_admin"]', 1850, 150, NOW(), NOW()),
('mb-step-settlement', 'workflow-mortgage-broker', 'settlement', 'Settlement', NULL, 'green', 'NORMAL', 12, '["accountant", "admin", "super_admin"]', 2050, 150, NOW(), NOW()),
('mb-step-declined', 'workflow-mortgage-broker', 'declined', 'Declined', NULL, 'red', 'END', 13, '["accountant", "admin", "super_admin"]', 1650, 300, NOW(), NOW()),
('mb-step-admin-review', 'workflow-mortgage-broker', 'admin_review', 'Admin Review', NULL, 'purple', 'NORMAL', 14, '["admin", "super_admin"]', 2150, 150, NOW(), NOW()),
('mb-step-completed', 'workflow-mortgage-broker', 'completed', 'Completed', NULL, 'green', 'END', 15, '["accountant", "admin", "super_admin"]', 2250, 150, NOW(), NOW()),

-- Default Workflow - Admin Review Step
('step-admin-review', 'default-workflow', 'admin_review', 'Admin Review', NULL, 'purple', 'NORMAL', 7, '["admin", "super_admin"]', 800, 250, NOW(), NOW())
;

-- =============================================================================
-- 9. WORKFLOW TRANSITIONS (connections between workflow steps)
-- =============================================================================

-- Default Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('trans-1', 'default-workflow', 'step-pending', 'step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-2', 'default-workflow', 'step-invoice-raised', 'step-assigned', 'Assign', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-3', 'default-workflow', 'step-assigned', 'step-processing', 'Start Processing', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-4', 'default-workflow', 'step-processing', 'step-query-raised', 'Raise Query', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-5', 'default-workflow', 'step-query-raised', 'step-review', 'Client Responded', NULL, false, false, false, '["user"]', true, NOW()),
('trans-6', 'default-workflow', 'step-review', 'step-processing', 'Resume Work', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-7', 'default-workflow', 'step-processing', 'step-completed', 'Complete', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-8', 'default-workflow', 'step-processing', 'step-admin-review', 'Submit for Admin Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-9', 'default-workflow', 'step-admin-review', 'step-processing', 'Request Changes', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('trans-10', 'default-workflow', 'step-admin-review', 'step-completed', 'Approve & Complete', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW());

-- Tax Agent Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('tax-t1', 'workflow-tax-agent', 'tax-step-pending', 'tax-step-docs-requested', 'Request Documents', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t2', 'workflow-tax-agent', 'tax-step-docs-requested', 'tax-step-docs-received', 'Documents Received', NULL, false, false, false, '["admin", "accountant", "super_admin", "user", "senior_accountant"]', true, NOW()),
('tax-t3', 'workflow-tax-agent', 'tax-step-docs-received', 'tax-step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t4', 'workflow-tax-agent', 'tax-step-invoice-raised', 'tax-step-assigned', 'Assign Accountant', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t5', 'workflow-tax-agent', 'tax-step-assigned', 'tax-step-preparation', 'Start Preparation', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t6', 'workflow-tax-agent', 'tax-step-preparation', 'tax-step-query', 'Raise Query', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t7', 'workflow-tax-agent', 'tax-step-query', 'tax-step-review', 'Client Responded', NULL, false, false, false, '["user"]', true, NOW()),
('tax-t8', 'workflow-tax-agent', 'tax-step-review', 'tax-step-preparation', 'Resume Preparation', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t9', 'workflow-tax-agent', 'tax-step-preparation', 'tax-step-lodgement', 'Ready for Lodgement', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t10', 'workflow-tax-agent', 'tax-step-lodgement', 'tax-step-lodged', 'Lodge with ATO', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t11', 'workflow-tax-agent', 'tax-step-lodged', 'tax-step-completed', 'Complete', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t12', 'workflow-tax-agent', 'tax-step-review', 'tax-step-lodgement', 'Client Approved', NULL, false, false, false, '["user"]', true, NOW()),
('tax-t13', 'workflow-tax-agent', 'tax-step-lodged', 'tax-step-admin-review', 'Submit for Admin Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('tax-t16', 'workflow-tax-agent', 'tax-step-preparation', 'tax-step-admin-review', 'Escalate to Admin', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW());

-- BAS Agent Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('bas-t1', 'workflow-bas-agent', 'bas-step-pending', 'bas-step-data-collection', 'Request Data', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t2', 'workflow-bas-agent', 'bas-step-data-collection', 'bas-step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t3', 'workflow-bas-agent', 'bas-step-invoice-raised', 'bas-step-assigned', 'Assign', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t4', 'workflow-bas-agent', 'bas-step-assigned', 'bas-step-reconciliation', 'Start Reconciliation', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t5', 'workflow-bas-agent', 'bas-step-reconciliation', 'bas-step-preparation', 'Prepare BAS', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t6', 'workflow-bas-agent', 'bas-step-preparation', 'bas-step-query', 'Raise Query', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t7', 'workflow-bas-agent', 'bas-step-query', 'bas-step-preparation', 'Query Resolved', NULL, false, false, false, '["accountant", "admin", "super_admin", "user", "senior_accountant"]', true, NOW()),
('bas-t8', 'workflow-bas-agent', 'bas-step-preparation', 'bas-step-review', 'Submit for Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t9', 'workflow-bas-agent', 'bas-step-review', 'bas-step-lodged', 'Lodge BAS', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t10', 'workflow-bas-agent', 'bas-step-lodged', 'bas-step-completed', 'Complete', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('bas-t14', 'workflow-bas-agent', 'bas-step-preparation', 'bas-step-admin-review', 'Escalate to Admin', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW());

-- SMSF Auditor Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('aud-t1', 'workflow-auditor', 'aud-step-pending', 'aud-step-engagement', 'Send Engagement Letter', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t2', 'workflow-auditor', 'aud-step-engagement', 'aud-step-docs-requested', 'Request Documents', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t3', 'workflow-auditor', 'aud-step-docs-requested', 'aud-step-docs-received', 'Documents Received', NULL, false, false, false, '["admin", "accountant", "super_admin", "user", "senior_accountant"]', true, NOW()),
('aud-t4', 'workflow-auditor', 'aud-step-docs-received', 'aud-step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t5', 'workflow-auditor', 'aud-step-invoice-raised', 'aud-step-assigned', 'Assign Auditor', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t6', 'workflow-auditor', 'aud-step-assigned', 'aud-step-fieldwork', 'Start Fieldwork', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t7', 'workflow-auditor', 'aud-step-fieldwork', 'aud-step-query', 'Raise Query', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t8', 'workflow-auditor', 'aud-step-query', 'aud-step-fieldwork', 'Query Resolved', NULL, false, false, false, '["accountant", "admin", "super_admin", "user", "senior_accountant"]', true, NOW()),
('aud-t9', 'workflow-auditor', 'aud-step-fieldwork', 'aud-step-draft-report', 'Prepare Draft Report', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t10', 'workflow-auditor', 'aud-step-draft-report', 'aud-step-management-review', 'Submit for Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t11', 'workflow-auditor', 'aud-step-management-review', 'aud-step-draft-report', 'Request Changes', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t12', 'workflow-auditor', 'aud-step-management-review', 'aud-step-final-report', 'Approve & Issue', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('aud-t13', 'workflow-auditor', 'aud-step-final-report', 'aud-step-completed', 'Complete', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW());

-- Bookkeeper Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('book-t1', 'workflow-bookkeeper', 'book-step-pending', 'book-step-access-setup', 'Setup Access', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('book-t2', 'workflow-bookkeeper', 'book-step-access-setup', 'book-step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t3', 'workflow-bookkeeper', 'book-step-invoice-raised', 'book-step-assigned', 'Assign', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t4', 'workflow-bookkeeper', 'book-step-assigned', 'book-step-processing', 'Start Processing', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t5', 'workflow-bookkeeper', 'book-step-processing', 'book-step-query', 'Raise Query', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t6', 'workflow-bookkeeper', 'book-step-query', 'book-step-processing', 'Query Resolved', NULL, false, false, false, '["accountant", "admin", "super_admin", "user", "senior_accountant"]', true, NOW()),
('book-t7', 'workflow-bookkeeper', 'book-step-processing', 'book-step-review', 'Submit for Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t8', 'workflow-bookkeeper', 'book-step-review', 'book-step-processing', 'Request Changes', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t9', 'workflow-bookkeeper', 'book-step-review', 'book-step-client-approval', 'Send for Approval', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t10', 'workflow-bookkeeper', 'book-step-client-approval', 'book-step-completed', 'Approve', NULL, false, false, false, '["user"]', true, NOW()),
('book-t11', 'workflow-bookkeeper', 'book-step-client-approval', 'book-step-processing', 'Request Changes', NULL, false, false, false, '["user"]', true, NOW()),
('book-t14', 'workflow-bookkeeper', 'book-step-admin-review', 'book-step-completed', 'Approve & Complete', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('book-t15', 'workflow-bookkeeper', 'book-step-processing', 'book-step-admin-review', 'Escalate to Admin', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW());

-- Financial Planner Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('fp-t1', 'workflow-financial-planner', 'fp-step-pending', 'fp-step-discovery', 'Schedule Discovery', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t2', 'workflow-financial-planner', 'fp-step-discovery', 'fp-step-fact-find', 'Send Fact Find', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t3', 'workflow-financial-planner', 'fp-step-fact-find', 'fp-step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t4', 'workflow-financial-planner', 'fp-step-invoice-raised', 'fp-step-assigned', 'Assign Planner', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t5', 'workflow-financial-planner', 'fp-step-assigned', 'fp-step-analysis', 'Start Analysis', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t6', 'workflow-financial-planner', 'fp-step-analysis', 'fp-step-soa-prep', 'Prepare SOA', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t7', 'workflow-financial-planner', 'fp-step-soa-prep', 'fp-step-compliance-review', 'Submit for Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t8', 'workflow-financial-planner', 'fp-step-compliance-review', 'fp-step-soa-prep', 'Request Changes', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t9', 'workflow-financial-planner', 'fp-step-compliance-review', 'fp-step-presentation', 'Approve & Present', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t10', 'workflow-financial-planner', 'fp-step-presentation', 'fp-step-query', 'Client Query', NULL, false, false, false, '["user"]', true, NOW()),
('fp-t11', 'workflow-financial-planner', 'fp-step-query', 'fp-step-presentation', 'Query Resolved', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t12', 'workflow-financial-planner', 'fp-step-presentation', 'fp-step-implementation', 'Client Accepted', NULL, false, false, false, '["user", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t13', 'workflow-financial-planner', 'fp-step-implementation', 'fp-step-completed', 'Complete', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t14', 'workflow-financial-planner', 'fp-step-implementation', 'fp-step-admin-review', 'Submit for Admin Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t16', 'workflow-financial-planner', 'fp-step-admin-review', 'fp-step-completed', 'Approve & Complete', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('fp-t17', 'workflow-financial-planner', 'fp-step-analysis', 'fp-step-admin-review', 'Escalate to Admin', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW());

-- Mortgage Broker Workflow Transitions
INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, description, requires_invoice_raised, requires_invoice_paid, requires_assignment, allowed_roles, send_notification, created_at) VALUES
('mb-t1', 'workflow-mortgage-broker', 'mb-step-pending', 'mb-step-consultation', 'Schedule Consultation', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t2', 'workflow-mortgage-broker', 'mb-step-consultation', 'mb-step-docs-collection', 'Request Documents', NULL, false, false, false, '["admin", "accountant", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t3', 'workflow-mortgage-broker', 'mb-step-docs-collection', 'mb-step-serviceability', 'Assess Serviceability', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t4', 'workflow-mortgage-broker', 'mb-step-serviceability', 'mb-step-product-selection', 'Select Products', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t5', 'workflow-mortgage-broker', 'mb-step-product-selection', 'mb-step-invoice-raised', 'Raise Invoice', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t6', 'workflow-mortgage-broker', 'mb-step-invoice-raised', 'mb-step-application', 'Submit Application', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t7', 'workflow-mortgage-broker', 'mb-step-application', 'mb-step-assessment', 'Lender Assessing', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t8', 'workflow-mortgage-broker', 'mb-step-assessment', 'mb-step-query', 'Info Required', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t9', 'workflow-mortgage-broker', 'mb-step-query', 'mb-step-assessment', 'Info Provided', NULL, false, false, false, '["accountant", "admin", "super_admin", "user", "senior_accountant"]', true, NOW()),
('mb-t10', 'workflow-mortgage-broker', 'mb-step-assessment', 'mb-step-conditional', 'Conditional Approved', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t11', 'workflow-mortgage-broker', 'mb-step-assessment', 'mb-step-declined', 'Declined', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t12', 'workflow-mortgage-broker', 'mb-step-conditional', 'mb-step-unconditional', 'Unconditional Approved', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t13', 'workflow-mortgage-broker', 'mb-step-unconditional', 'mb-step-settlement', 'Proceed to Settlement', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t14', 'workflow-mortgage-broker', 'mb-step-settlement', 'mb-step-completed', 'Settlement Complete', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t15', 'workflow-mortgage-broker', 'mb-step-settlement', 'mb-step-admin-review', 'Submit for Admin Review', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t16', 'workflow-mortgage-broker', 'mb-step-admin-review', 'mb-step-application', 'Request Changes', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t17', 'workflow-mortgage-broker', 'mb-step-admin-review', 'mb-step-completed', 'Approve & Complete', NULL, false, false, false, '["admin", "super_admin", "senior_accountant"]', true, NOW()),
('mb-t18', 'workflow-mortgage-broker', 'mb-step-assessment', 'mb-step-admin-review', 'Escalate to Admin', NULL, false, false, false, '["accountant", "admin", "super_admin", "senior_accountant"]', true, NOW());

-- =============================================================================
-- 10. SERVICES (Default/System services)
-- =============================================================================
INSERT INTO services (id, name, description, category, base_price, is_active, is_default, form_id, workflow_id, is_recurring, renewal_period_months, created_at, updated_at) VALUES
-- Tax Agent Services
(1, 'Individual Tax Return', 'Annual individual tax return preparation and lodgement with ATO', 'tax_agent', 350.00, true, true, NULL, 'workflow-tax-agent', true, 12, NOW(), NOW()),
(2, 'Business Activity Statement (BAS)', 'Quarterly or monthly BAS preparation and lodgement', 'bas_agent', 300.00, true, true, NULL, 'workflow-bas-agent', false, NULL, NOW(), NOW()),
(3, 'Investment Rental Property', 'Tax return schedule for rental property income and deductions', 'tax_agent', 200.00, true, true, NULL, 'workflow-tax-agent', false, NULL, NOW(), NOW()),
(4, 'Company Tax Return', 'Annual company tax return preparation', 'tax_agent', 800.00, true, true, NULL, 'workflow-tax-agent', true, 12, NOW(), NOW()),
(5, 'Partnership Tax Return', 'Tax return preparation for partnerships', 'tax_agent', 600.00, true, true, NULL, 'workflow-tax-agent', true, 12, NOW(), NOW()),
(6, 'Trust Tax Return', 'Tax return preparation for trusts including distribution statements', 'tax_agent', 750.00, true, true, NULL, 'workflow-tax-agent', true, 12, NOW(), NOW()),
(7, 'SMSF Tax Return', 'Annual tax return preparation for Self-Managed Super Fund', 'tax_agent', 500.00, true, true, NULL, 'workflow-tax-agent', true, 12, NOW(), NOW()),
(8, 'Business Tax Return - Sole Trader', 'Tax return preparation for sole traders', 'tax_agent', 350.00, true, true, NULL, 'workflow-tax-agent', true, 12, NOW(), NOW()),

-- SMSF Audit Services
(10, 'SMSF Annual Audit', 'Complete annual audit of Self-Managed Super Fund', 'auditor', 1500.00, true, true, NULL, 'workflow-auditor', true, 12, NOW(), NOW()),
(11, 'SMSF Compliance Audit', 'Compliance-focused audit ensuring SMSF meets all regulatory requirements', 'auditor', 1200.00, true, true, NULL, 'workflow-auditor', true, 12, NOW(), NOW()),
(12, 'SMSF Establishment Audit', 'Initial audit for newly established SMSFs', 'auditor', 800.00, true, true, NULL, 'workflow-auditor', false, NULL, NOW(), NOW()),
(13, 'SMSF Wind-Up Audit', 'Final audit for SMSFs being wound up', 'auditor', 1000.00, true, true, NULL, 'workflow-auditor', false, NULL, NOW(), NOW()),

-- Financial Planning Services
(20, 'Comprehensive Financial Plan', 'Full financial planning including retirement, investment, insurance', 'financial_planner', 3500.00, true, true, NULL, 'workflow-financial-planner', false, NULL, NOW(), NOW()),
(21, 'Retirement Planning', 'Detailed retirement planning including super strategy', 'financial_planner', 1800.00, true, true, NULL, 'workflow-financial-planner', false, NULL, NOW(), NOW()),
(22, 'Investment Portfolio Review', 'Review of investment portfolio with recommendations', 'financial_planner', 800.00, true, true, NULL, 'workflow-financial-planner', true, 12, NOW(), NOW()),
(23, 'Superannuation Strategy', 'Strategic advice on super contributions and optimization', 'financial_planner', 1200.00, true, true, NULL, 'workflow-financial-planner', false, NULL, NOW(), NOW()),
(24, 'Insurance Needs Analysis', 'Comprehensive review of insurance needs', 'financial_planner', 600.00, true, true, NULL, 'workflow-financial-planner', false, NULL, NOW(), NOW()),

-- Mortgage Broker Services
(30, 'Home Loan - New Purchase', 'Full service for home purchase including loan comparison', 'mortgage_broker', 0.00, true, true, NULL, 'workflow-mortgage-broker', false, NULL, NOW(), NOW()),
(31, 'Home Loan Refinance', 'Refinance existing home loan for better rates', 'mortgage_broker', 0.00, true, true, NULL, 'workflow-mortgage-broker', false, NULL, NOW(), NOW()),
(32, 'Investment Property Loan', 'Loan arrangement for investment property', 'mortgage_broker', 0.00, true, true, NULL, 'workflow-mortgage-broker', false, NULL, NOW(), NOW()),
(33, 'Construction Loan', 'Specialized loan for new home construction', 'mortgage_broker', 0.00, true, true, NULL, 'workflow-mortgage-broker', false, NULL, NOW(), NOW()),
(34, 'Commercial Property Loan', 'Business and commercial property financing', 'mortgage_broker', 0.00, true, true, NULL, 'workflow-mortgage-broker', false, NULL, NOW(), NOW()),

-- Bookkeeping Services
(40, 'Monthly Bookkeeping', 'Complete monthly bookkeeping including reconciliation', 'bookkeeper', 400.00, true, true, NULL, 'workflow-bookkeeper', true, 1, NOW(), NOW()),
(41, 'Quarterly Bookkeeping', 'Quarterly bookkeeping package for smaller businesses', 'bookkeeper', 350.00, true, true, NULL, 'workflow-bookkeeper', true, 3, NOW(), NOW()),
(42, 'Payroll Processing - Monthly', 'Monthly payroll processing including STP reporting', 'bookkeeper', 180.00, true, true, NULL, 'workflow-bookkeeper', true, 1, NOW(), NOW()),

-- BAS Agent Services
(50, 'BAS Lodgement - Quarterly', 'Quarterly BAS preparation and lodgement', 'bas_agent', 180.00, true, true, NULL, 'workflow-bas-agent', true, 3, NOW(), NOW()),
(51, 'BAS Lodgement - Monthly', 'Monthly BAS preparation and lodgement', 'bas_agent', 150.00, true, true, NULL, 'workflow-bas-agent', true, 1, NOW(), NOW()),
(52, 'GST Registration', 'GST registration with the ATO', 'bas_agent', 100.00, true, true, NULL, 'workflow-bas-agent', false, NULL, NOW(), NOW()),
(53, 'PAYG Withholding Setup', 'Setup of PAYG withholding obligations', 'bas_agent', 150.00, true, true, NULL, 'workflow-bas-agent', false, NULL, NOW(), NOW()),

-- Company Registration
(60, 'Company Incorporation', 'New company registration with ASIC', 'tax_agent', 800.00, true, true, NULL, 'workflow-tax-agent', false, NULL, NOW(), NOW()),
(61, 'Trust Establishment', 'Setup of new trust including trust deed', 'tax_agent', 1200.00, true, true, NULL, 'workflow-tax-agent', false, NULL, NOW(), NOW()),
(62, 'SMSF Establishment', 'Setup of new Self-Managed Super Fund', 'tax_agent', 1500.00, true, true, NULL, 'workflow-tax-agent', false, NULL, NOW(), NOW());

SELECT setval('services_id_seq', (SELECT MAX(id) FROM services));

-- =============================================================================
-- 10. EMAIL TEMPLATES (System defaults - company_id IS NULL)
-- =============================================================================
INSERT INTO email_templates (id, name, slug, subject, body_html, variables, company_id, is_active, created_at) VALUES
(1, 'Welcome Email', 'welcome', 'Welcome to {company_name}!',
'<p>Dear {client_name},</p>
<p>Welcome to {company_name}! We''re excited to have you as our client.</p>
<p>Your account has been created. Please login at: {portal_link}</p>
<p>Best regards,<br>{company_name}</p>',
'["client_name", "client_email", "company_name", "portal_link"]', NULL, true, NOW()),

(2, 'Invoice Email', 'invoice', 'Invoice #{invoice_number} from {company_name}',
'<p>Dear {client_name},</p>
<p>Please find attached your invoice for {service_name}.</p>
<p><strong>Invoice Details:</strong><br>
Invoice Number: {invoice_number}<br>
Amount Due: {amount}<br>
Due Date: {due_date}</p>
<p>Pay online: <a href="{payment_link}">Pay Now</a></p>
<p>Best regards,<br>{company_name}</p>',
'["client_name", "service_name", "invoice_number", "amount", "due_date", "payment_link", "company_name"]', NULL, true, NOW()),

(3, 'Payment Reminder', 'payment_reminder', 'Payment Reminder - Invoice #{invoice_number}',
'<p>Dear {client_name},</p>
<p>This is a friendly reminder that payment for Invoice #{invoice_number} is due.</p>
<p>Amount Due: {amount}<br>Due Date: {due_date}</p>
<p><a href="{payment_link}">Pay Now</a></p>
<p>Best regards,<br>{company_name}</p>',
'["client_name", "invoice_number", "amount", "due_date", "payment_link", "company_name"]', NULL, true, NOW()),

(4, 'Document Request', 'document_request', 'Documents Required for {service_name}',
'<p>Dear {client_name},</p>
<p>To proceed with your {service_name}, we require the following documents:</p>
<p>{document_list}</p>
<p>Please upload via: <a href="{portal_link}">Upload Documents</a></p>
<p>Best regards,<br>{accountant_name}<br>{company_name}</p>',
'["client_name", "service_name", "document_list", "portal_link", "accountant_name", "company_name"]', NULL, true, NOW()),

(5, 'Service Completed', 'service_completed', 'Your {service_name} is Complete',
'<p>Dear {client_name},</p>
<p>Great news! Your {service_name} has been completed.</p>
<p>{completion_notes}</p>
<p>View details: <a href="{portal_link}">View Details</a></p>
<p>Thank you for choosing {company_name}.</p>
<p>Best regards,<br>{accountant_name}<br>{company_name}</p>',
'["client_name", "service_name", "completion_notes", "portal_link", "accountant_name", "company_name"]', NULL, true, NOW()),

(6, 'Query Raised', 'query_raised', 'Response Required - {service_name}',
'<p>Dear {client_name},</p>
<p>We have a question regarding your {service_name}:</p>
<p><strong>Query:</strong><br>{query_message}</p>
<p>Please respond: <a href="{portal_link}">Respond Now</a></p>
<p>Best regards,<br>{accountant_name}<br>{company_name}</p>',
'["client_name", "service_name", "query_message", "portal_link", "accountant_name", "company_name"]', NULL, true, NOW()),

(7, 'Password Reset', 'password_reset', 'Password Reset Request - {company_name}',
'<p>Dear {client_name},</p>
<p>We received a request to reset your password.</p>
<p>Reset code: <strong>{otp}</strong></p>
<p>This code expires in 10 minutes.</p>
<p>If you didn''t request this, please ignore this email.</p>
<p>Best regards,<br>{company_name}</p>',
'["client_name", "otp", "company_name"]', NULL, true, NOW()),

(8, 'User Invitation', 'user_invitation', 'You''ve Been Invited to {company_name}',
'<p>Hello {user_name},</p>
<p>You have been invited to join {company_name}.</p>
<p><strong>Login Details:</strong><br>
Email: {email}<br>
Temporary Password: {password}</p>
<p><a href="{login_url}">Login Now</a></p>
<p>Please change your password after first login.</p>
<p>Best regards,<br>{company_name}</p>',
'["user_name", "company_name", "email", "password", "login_url"]', NULL, true, NOW())

;

SELECT setval('email_templates_id_seq', (SELECT MAX(id) FROM email_templates));

-- =============================================================================
-- 11. FORMS (System default forms - company_id IS NULL)
-- =============================================================================
INSERT INTO forms (id, name, description, form_type, is_active, created_by_id, created_at, updated_at, company_id, is_default, status) VALUES
(1, 'Individual Tax Return Information', 'Please provide the following information for your tax return', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(2, 'BAS Information Form', 'Provide your business activity details for the period', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(3, 'Rental Property Information', 'Details about your investment property for tax purposes', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(4, 'SMSF Setup Application', 'Information required to establish your Self-Managed Super Fund', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(5, 'Company Registration Form', 'Information required to register your new company', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(6, 'Company Incorporation Form', 'Complete this form to register your new company with ASIC', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(7, 'SMSF Setup Form', 'Complete this form to establish your Self-Managed Super Fund', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(8, 'SMSF Annual Compliance Questionnaire', 'Annual compliance questionnaire for Self-Managed Super Fund clients', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(9, 'Company Annual Compliance Questionnaire', 'Annual compliance questionnaire for company clients', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published'),
(11, 'SMSF Annual Audit Form', 'Complete this form and upload all required documents for your SMSF Annual Audit', 'service', true, NULL, NOW(), NOW(), NULL, true, 'published')
;

SELECT setval('forms_id_seq', (SELECT MAX(id) FROM forms));

-- =============================================================================
-- 12. FORM QUESTIONS (for system default forms)
-- =============================================================================
-- Individual Tax Return (Form 1)
INSERT INTO form_questions (id, form_id, question_text, question_type, is_required, options, placeholder, help_text, "order", created_at) VALUES
(1, 1, 'What is your Tax File Number (TFN)?', 'text', true, NULL, 'XXX XXX XXX', NULL, 0, NOW()),
(2, 1, 'What is your date of birth?', 'date', true, NULL, NULL, NULL, 1, NOW()),
(3, 1, 'What is your occupation?', 'text', true, NULL, NULL, NULL, 2, NOW()),
(4, 1, 'Did you have any income from employment?', 'radio', true, '["Yes", "No"]', NULL, NULL, 3, NOW()),
(5, 1, 'Upload your PAYG Payment Summary / Income Statement', 'file', false, NULL, NULL, 'You can find this in your myGov account', 4, NOW()),
(6, 1, 'Did you have any bank interest income?', 'radio', true, '["Yes", "No"]', NULL, NULL, 5, NOW()),
(7, 1, 'Did you have any dividend income?', 'radio', true, '["Yes", "No"]', NULL, NULL, 6, NOW()),
(8, 1, 'Do you have private health insurance?', 'radio', true, '["Yes", "No"]', NULL, NULL, 7, NOW()),
(9, 1, 'Upload your Private Health Insurance Statement', 'file', false, NULL, NULL, NULL, 8, NOW()),
(10, 1, 'What work-related expenses do you want to claim?', 'multiselect', false, '["Work from home expenses", "Vehicle/Travel expenses", "Uniform/Clothing", "Tools and equipment", "Self-education", "Other"]', NULL, NULL, 9, NOW()),
(11, 1, 'Please provide details of any other deductions', 'textarea', false, NULL, 'List any additional deductions', NULL, 10, NOW()),

-- BAS Form (Form 2)
(12, 2, 'What is your ABN?', 'text', true, NULL, 'XX XXX XXX XXX', NULL, 0, NOW()),
(13, 2, 'What period is this BAS for?', 'select', true, '["July-September (Q1)", "October-December (Q2)", "January-March (Q3)", "April-June (Q4)", "Monthly"]', NULL, NULL, 1, NOW()),
(14, 2, 'Are you registered for GST?', 'radio', true, '["Yes", "No"]', NULL, NULL, 2, NOW()),
(15, 2, 'Total sales/income for the period (including GST)', 'number', true, NULL, '0.00', NULL, 3, NOW()),
(16, 2, 'Total purchases/expenses for the period (including GST)', 'number', true, NULL, '0.00', NULL, 4, NOW()),
(17, 2, 'Do you have PAYG withholding obligations?', 'radio', true, '["Yes", "No"]', NULL, NULL, 5, NOW()),
(18, 2, 'Total wages paid for the period', 'number', false, NULL, '0.00', NULL, 6, NOW()),
(19, 2, 'Total PAYG withheld from wages', 'number', false, NULL, '0.00', NULL, 7, NOW()),
(20, 2, 'Upload your sales report/invoices', 'file', false, NULL, NULL, NULL, 8, NOW()),
(21, 2, 'Upload your purchase invoices/receipts', 'file', false, NULL, NULL, NULL, 9, NOW()),
(22, 2, 'Any additional notes or information', 'textarea', false, NULL, NULL, NULL, 10, NOW()),

-- Rental Property Form (Form 3)
(23, 3, 'Property address', 'textarea', true, NULL, 'Full address of the rental property', NULL, 0, NOW()),
(24, 3, 'When did you purchase this property?', 'date', true, NULL, NULL, NULL, 1, NOW()),
(25, 3, 'What was the purchase price?', 'number', true, NULL, '0.00', NULL, 2, NOW()),
(26, 3, 'How many weeks was the property rented this year?', 'number', true, NULL, '52', NULL, 3, NOW()),
(27, 3, 'Total rental income received', 'number', true, NULL, '0.00', NULL, 4, NOW()),
(28, 3, 'Is the property managed by an agent?', 'radio', true, '["Yes - Full management", "Yes - Letting only", "No - Self managed"]', NULL, NULL, 5, NOW()),
(29, 3, 'Property management fees paid', 'number', false, NULL, '0.00', NULL, 6, NOW()),
(30, 3, 'Council rates paid', 'number', false, NULL, '0.00', NULL, 7, NOW()),
(31, 3, 'Water rates paid', 'number', false, NULL, '0.00', NULL, 8, NOW()),
(32, 3, 'Insurance premium paid', 'number', false, NULL, '0.00', NULL, 9, NOW()),
(33, 3, 'Interest on loan paid', 'number', false, NULL, '0.00', NULL, 10, NOW()),
(34, 3, 'Repairs and maintenance costs', 'number', false, NULL, '0.00', NULL, 11, NOW()),
(35, 3, 'Upload rental income statement from agent', 'file', false, NULL, NULL, NULL, 12, NOW()),
(36, 3, 'Upload depreciation schedule (if available)', 'file', false, NULL, NULL, NULL, 13, NOW()),
(37, 3, 'Any capital improvements made this year?', 'textarea', false, NULL, NULL, 'List any renovations or improvements with costs', 14, NOW()),

-- SMSF Setup Application (Form 4)
(38, 4, 'Proposed fund name', 'text', true, NULL, 'e.g., Smith Family Superannuation Fund', NULL, 0, NOW()),
(39, 4, 'Trustee structure', 'radio', true, '["Individual trustees", "Corporate trustee"]', NULL, 'Corporate trustee recommended for better asset protection', 1, NOW()),
(40, 4, 'Number of members', 'select', true, '["1", "2", "3", "4"]', NULL, NULL, 2, NOW()),
(41, 4, 'Member 1 - Full name', 'text', true, NULL, NULL, NULL, 3, NOW()),
(42, 4, 'Member 1 - Date of birth', 'date', true, NULL, NULL, NULL, 4, NOW()),
(43, 4, 'Member 1 - TFN', 'text', true, NULL, NULL, NULL, 5, NOW()),
(44, 4, 'Member 1 - Current super fund name', 'text', false, NULL, NULL, 'Fund you are rolling over from', 6, NOW()),
(45, 4, 'Member 1 - Approximate rollover amount', 'number', false, NULL, '0.00', NULL, 7, NOW()),
(46, 4, 'Member 2 - Full name (if applicable)', 'text', false, NULL, NULL, NULL, 8, NOW()),
(47, 4, 'Member 2 - Date of birth', 'date', false, NULL, NULL, NULL, 9, NOW()),
(48, 4, 'Member 2 - TFN', 'text', false, NULL, NULL, NULL, 10, NOW()),
(49, 4, 'Investment strategy preferences', 'multiselect', true, '["Australian shares", "International shares", "Property", "Cash/Term deposits", "Bonds", "Cryptocurrency"]', NULL, NULL, 11, NOW()),
(50, 4, 'Do you plan to borrow to invest (LRBA)?', 'radio', true, '["Yes", "No", "Not sure"]', NULL, NULL, 12, NOW()),
(51, 4, 'Upload ID documents for all members', 'file', true, NULL, NULL, 'Passport or Drivers License', 13, NOW()),
(52, 4, 'Any specific questions or requirements?', 'textarea', false, NULL, NULL, NULL, 14, NOW()),

-- Company Registration Form (Form 5)
(53, 5, 'Proposed company name (Option 1)', 'text', true, NULL, NULL, 'Must end with Pty Ltd', 0, NOW()),
(54, 5, 'Proposed company name (Option 2)', 'text', false, NULL, NULL, 'Backup name in case first choice is taken', 1, NOW()),
(55, 5, 'Company type', 'radio', true, '["Proprietary Limited (Pty Ltd)", "Public Company (Ltd)"]', NULL, NULL, 2, NOW()),
(56, 5, 'Principal business activity', 'text', true, NULL, 'e.g., IT Consulting, Construction, Retail', NULL, 3, NOW()),
(57, 5, 'Registered office address', 'textarea', true, NULL, NULL, 'Must be a physical address in Australia', 4, NOW()),
(58, 5, 'Principal place of business', 'textarea', true, NULL, NULL, NULL, 5, NOW()),
(59, 5, 'Number of directors', 'select', true, '["1", "2", "3", "4", "5+"]', NULL, NULL, 6, NOW()),
(60, 5, 'Director 1 - Full name', 'text', true, NULL, NULL, NULL, 7, NOW()),
(61, 5, 'Director 1 - Date of birth', 'date', true, NULL, NULL, NULL, 8, NOW()),
(62, 5, 'Director 1 - Residential address', 'textarea', true, NULL, NULL, NULL, 9, NOW()),
(63, 5, 'Director 1 - Place of birth (City, Country)', 'text', true, NULL, NULL, NULL, 10, NOW()),
(64, 5, 'Director 2 - Full name (if applicable)', 'text', false, NULL, NULL, NULL, 11, NOW()),
(65, 5, 'Number of shares to be issued', 'number', true, NULL, '100', NULL, 12, NOW()),
(66, 5, 'Share price', 'number', true, NULL, '1.00', NULL, 13, NOW()),
(67, 5, 'Shareholder 1 - Name', 'text', true, NULL, NULL, NULL, 14, NOW()),
(68, 5, 'Shareholder 1 - Number of shares', 'number', true, NULL, NULL, NULL, 15, NOW()),
(69, 5, 'Do you need GST registration?', 'radio', true, '["Yes", "No", "Not sure"]', NULL, NULL, 16, NOW()),
(70, 5, 'Do you need to register as an employer?', 'radio', true, '["Yes", "No", "Not sure"]', NULL, NULL, 17, NOW()),
(71, 5, 'Upload ID for all directors', 'file', true, NULL, NULL, NULL, 18, NOW())
;

SELECT setval('form_questions_id_seq', (SELECT MAX(id) FROM form_questions));

-- =============================================================================
-- 13. SMSF QUESTIONS (for FitForMe assessment)
-- =============================================================================
INSERT INTO smsf_questions (id, text, category, type, weight, "order", is_active, options, created_at, updated_at) VALUES
(1, 'Do you understand that only properly licensed professionals can provide personal advice recommending an SMSF, and that you should receive written advice (e.g. SOA) if personal advice is given?', 'Am I Right for SMSF?', 'Compliance', 0.05, 1, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(2, 'Do you understand that SMSF investments must comply with the sole purpose test, arm''s-length rules and other restrictions (e.g. on in-house assets and related-party transactions)?', 'Am I Right for SMSF?', 'Compliance', 0.05, 2, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(3, 'Are you aware the ATO is the regulator and that it takes a strong stance on illegal early access, related-party dealings and non-arm''s-length arrangements?', 'Am I Right for SMSF?', 'Compliance', 0.05, 3, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(4, 'Do any member/s of your proposed SMSF have a history of bankruptcy, serious credit issues or legal disputes that might affect their eligibility or trustee suitability?', 'Am I Right for SMSF?', 'Compliance', 0.05, 4, true, '["No", "Not Sure", "Yes"]', NOW(), NOW()),
(5, 'Do you stay updated on superannuation regulations and compliance requirements for SMSFs?', 'Am I Right for SMSF?', 'Compliance', 0.03, 5, true, '["Yes", "Sometime", "No"]', NOW(), NOW()),
(6, 'Have you set clear financial goals for your retirement and actively monitor your progress?', 'Am I Right for SMSF?', 'Financial', 0.03, 6, true, '["Yes", "Kind of", "No"]', NOW(), NOW()),
(7, 'Do you currently have a will, powers of attorney and any binding or non-binding death benefit nominations in place in your existing funds?', 'Am I Right for SMSF?', 'Governance', 0.05, 7, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(8, 'What experience do you (and other proposed trustees) have with investing, tax, trusts, or running a small business or entity in Australia?', 'Am I Right for SMSF?', 'Governance', 0.04, 8, true, '["I am a Pro", "Little/ Some experience", "No experience at all"]', NOW(), NOW()),
(9, 'How would you rate your overall understanding of SMSF rules, including the regulatory obligations and ongoing compliance responsibilities involved in running an SMSF?', 'Am I Right for SMSF?', 'Governance', 0.03, 9, true, '["Confident", "Comfortable", "Not Much"]', NOW(), NOW()),
(10, 'How much time per month can you realistically devote to managing the SMSF (reviewing investments, dealing with paperwork, keeping records, working with advisers)?', 'Am I Right for SMSF?', 'Governance', 0.02, 10, true, '["More than 6 Hours", "3-6 hours", "0-3 Hours"]', NOW(), NOW()),
(11, 'In general, do you tend to seek professional advice before making significant investment decisions?', 'Am I Right for SMSF?', 'Risk Appetite', 0.05, 11, true, '["Yes, always", "At times", "Not at all"]', NOW(), NOW()),
(12, 'Are you comfortable with the idea of taking risk to achieve better returns for your retirement by investing your Super money?', 'Am I Right for SMSF?', 'Risk Appetite', 0.05, 12, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(13, 'How important do you think it is for an SMSF to hold a diversified mix of assets (rather than just one or two major investments such as a single property)', 'Am I Right for SMSF?', 'Risk Appetite', 0.05, 13, true, '["Extremely Important", "Not Sure", "Not Important"]', NOW(), NOW()),
(14, 'If you are well guided on SMSF setup and its ongoing compliance by a subject matter expert (like an SMSF Accountant or a SMSF Specialist, how comfortable will you be to move ahead forming your own SMSF?', 'Am I Right for SMSF?', 'Risk Appetite', 0.02, 14, true, '["Yes, all set to go!", "Understand next steps first", "Need more time to think"]', NOW(), NOW()),
(15, 'Have you considered whether to use individual trustees or a corporate trustee, and do you understand some of the pros and cons of each?', 'Is SMSF Right for me?', 'Compliance', 0.04, 15, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(16, 'Are there any specific assets you want the SMSF to hold or invest in?', 'Is SMSF Right for me?', 'Financial', 0.00, 16, true, '["Yes, very clear on this.", "Not Sure", "Will need some advice"]', NOW(), NOW()),
(17, 'Do all potential members of your SMSF (including you) have basic insurances (like life, TPD, income protection insurance) in place?', 'Is SMSF Right for me?', 'Financial', 0.07, 17, true, '["Yes", "Not Sure", "No"]', NOW(), NOW()),
(18, 'What is the combined super balance (in AUD$) of all potential SMSF members if your SMSF was to be established today?', 'Is SMSF Right for me?', 'Financial', 0.07, 18, true, '["More than $250K", "$151K - $250K", "Under $150K"]', NOW(), NOW()),
(19, 'What is the approximate annual super contributions (in AUD $) of all potential SMSF members combined to come into your SMSF?', 'Is SMSF Right for me?', 'Financial', 0.07, 19, true, '["Greater than $25K", "Between $15K - $25K", "Upto $15K"]', NOW(), NOW()),
(20, 'What is the gross annual taxable income of your household combined? (Note: You can check your last tax return filed to provide a specific number in AUD $)', 'Is SMSF Right for me?', 'Financial', 0.07, 20, true, '["More than $190K", "Between $135K to $190K", "Upto $135K"]', NOW(), NOW()),
(21, 'What is the average age (in years) for each individual planning to be an SMSF member as of 30th June of previous year?', 'Is SMSF Right for me?', 'Financial', 0.07, 21, true, '["Between 19 - 40 years", "Between 41 - 50 years", "> 50 years"]', NOW(), NOW()),
(22, 'Have you sought a written professional financial advice (SOA) for forming an SMSF in last 6 months from today?', 'Is SMSF Right for me?', 'Financial', 0.03, 22, true, '["Yes", "Only verbal", "No"]', NOW(), NOW()),
(23, 'What type of support relationship are you looking for with Pointers Consulting in relation to your SMSF plan?', 'Is SMSF Right for me?', 'Governance', 0.00, 23, true, '["Just one-off discussion to understand SMSF basics", "Ongoing holistic support (SMSF Setup + ongoing annual compliance)", "Not Sure"]', NOW(), NOW()),
(24, 'How many members will be there in your SMSF, presuming you have decided to go ahead with the idea of setting up an SMSF?', 'Is SMSF Right for me?', 'Governance', 0.00, 24, true, '["Only 1 Member - Me!", "2 to 3 Members", "4 to 6 Members"]', NOW(), NOW()),
(25, 'How did you hear or come to know about SMSF and whether it is right for you or not?', 'Is SMSF Right for me?', 'Governance', 0.03, 25, true, '["Obtained Professional Advice (Written)", "Did my own research AND/OR Verbal professional advice taken", "Through a personal contact (like a friend, colleague etc.)"]', NOW(), NOW())
;

SELECT setval('smsf_questions_id_seq', (SELECT MAX(id) FROM smsf_questions));

COMMIT;

-- =============================================================================
-- VERIFICATION
-- =============================================================================
SELECT '========================================' as separator;
SELECT 'Seed completed successfully!' as status;
SELECT '========================================' as separator;
SELECT 'Roles: ' || COUNT(*) FROM roles;
SELECT 'Companies: ' || COUNT(*) FROM companies;
SELECT 'Users: ' || COUNT(*) FROM users;
SELECT 'System Statuses: ' || COUNT(*) FROM system_request_statuses;
SELECT 'Kanban Board Statuses: ' || COUNT(*) FROM company_request_statuses;
SELECT 'Currencies: ' || COUNT(*) FROM currencies;
SELECT 'Tax Types: ' || COUNT(*) FROM tax_types;
SELECT 'Workflows: ' || COUNT(*) FROM service_workflows;
SELECT 'Workflow Steps: ' || COUNT(*) FROM workflow_steps;
SELECT 'Workflow Transitions: ' || COUNT(*) FROM workflow_transitions;
SELECT 'Services: ' || COUNT(*) FROM services;
SELECT 'Email Templates: ' || COUNT(*) FROM email_templates;
SELECT 'Forms: ' || COUNT(*) FROM forms;
SELECT 'Form Questions: ' || COUNT(*) FROM form_questions;
SELECT 'SMSF Questions: ' || COUNT(*) FROM smsf_questions;
SELECT '========================================' as separator;
SELECT 'Admin Login: aggarwal.adarsh98@gmail.com / Big@200650078296' as admin_info;
