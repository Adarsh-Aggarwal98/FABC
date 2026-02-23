# Demo Test Environment

This document contains all the information needed to test the CRM application locally.

---

## Quick Start

```bash
# Start the application
docker-compose -f docker-compose.windows.yml up -d

# Run seed data (if not already done)
docker exec crm-backend python seed_test_data.py
```

**Access URLs:**
- Frontend: http://localhost:5174
- Backend API: http://localhost:5001

---

## Test User Accounts

All test accounts use the password: **`Demo@123`**

| Role | Email | Description |
|------|-------|-------------|
| Super Admin | superadmin@demo.com | Full system access, can manage all companies |
| Admin | admin@demo.com | Company admin, full access to company features |
| Senior Accountant | senior@demo.com | Team lead, all admin privileges except invoicing |
| Accountant | accountant1@demo.com | Regular accountant, assigned to senior@demo.com |
| Accountant | accountant2@demo.com | Regular accountant, assigned to senior@demo.com |
| External Accountant | external@demo.com | Limited access, external partner |
| Client | client1@demo.com | Bob BusinessOwner - owns 3 entities |
| Client | client2@demo.com | Alice Entrepreneur - owns 2 entities |
| Client | client3@demo.com | Charlie Contractor - owns 1 entity |

---

## Role Permissions

### Super Admin
- Access to all companies
- Manage all users across companies
- System-wide settings
- All admin features

### Admin
- Manage users within company
- Manage services, workflows, forms
- Create and manage invoices
- Company settings, branding, email templates
- View all analytics

### Senior Accountant
- All admin privileges EXCEPT:
  - Cannot create/manage invoices
  - Cannot access invoice settings
  - Cannot view Job Analytics
  - Cannot view Client Analytics
  - Cannot view revenue/invoice stats on Dashboard
- Can supervise accountants
- Can manage workflows, services, forms

### Accountant
- View assigned requests
- Update request status
- Add notes and time entries
- Communicate with clients
- View job analytics
- Cannot view revenue/invoice stats on Dashboard

### Client (User)
- Submit new service requests
- View own requests
- Respond to queries
- Upload documents
- Complete onboarding
- Dashboard shows only:
  - My Requests count
  - Queries to Answer
  - Pending Payments

### External Accountant
- Limited to assigned requests only
- Basic request updates
- Skips onboarding flow
- Dashboard shows only:
  - My Requests count
  - Queries to Answer
  - Pending Payments

---

## Test Client Entities

| Entity Name | Type | ABN | Owner |
|-------------|------|-----|-------|
| Bob's Construction Pty Ltd | Company | 11 222 333 444 | client1@demo.com |
| Bob Smith Family Trust | Trust | 11 222 333 445 | client1@demo.com |
| Smith Family SMSF | SMSF | 44 555 666 777 | client1@demo.com |
| Alice Tech Solutions | Sole Trader | 22 333 444 555 | client2@demo.com |
| Alice & Co Holdings | Company | 22 333 444 556 | client2@demo.com |
| Charlie Consulting | Sole Trader | 33 444 555 666 | client3@demo.com |

---

## Test Service Requests

Requests are created in various workflow statuses to demonstrate the Kanban board:

| Status | Count | Description |
|--------|-------|-------------|
| Pending | 2 | New requests, not yet assigned |
| Assigned | 2 | Assigned to accountant, collecting documents |
| In Progress | 3 | Actively being worked on |
| Under Review | 2 | Submitted for senior review |
| Query Raised | 2 | Waiting for client response |
| Lodgement | 1 | Ready to lodge with ATO |
| Invoicing | 1 | Work complete, generating invoice |
| Completed | 3 | Fully completed requests |
| On Hold | 1 | Temporarily paused |

---

## Testing Workflows

### 1. Test as Admin (admin@demo.com)
- View Dashboard with statistics
- Navigate to Kanban board (Requests page)
- Drag requests between columns
- Assign requests to accountants
- Create invoices for completed work
- Manage services and workflows
- View analytics

### 2. Test as Senior Accountant (senior@demo.com)
- Same as admin but NO invoice creation
- View team members under supervision
- Review work submitted by accountants
- Approve/reject work in review status

### 3. Test as Accountant (accountant1@demo.com)
- View assigned requests only
- Update request status
- Add time entries and notes
- Submit work for review
- Communicate with clients via queries

### 4. Test as Client (client1@demo.com)
- Complete onboarding flow (first login)
- View own entities and requests
- Submit new service requests
- Respond to queries
- Upload documents

---

## Supervisor Hierarchy

```
senior@demo.com (Senior Accountant)
├── accountant1@demo.com (Accountant)
├── accountant2@demo.com (Accountant)
└── [other accountants in company]
```

---

## API Endpoints for Testing

```bash
# Health check
curl http://localhost:5001/api/health

# Login (get token)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "Demo@123"}'

# Get requests (with auth token)
curl http://localhost:5001/api/requests \
  -H "Authorization: Bearer <token>"

# Get Kanban board data
curl http://localhost:5001/api/requests/kanban \
  -H "Authorization: Bearer <token>"
```

---

## Database Access

```bash
# Connect to database
docker exec -it crm-db psql -U postgres -d accountant_crm

# Useful queries
SELECT email, r.name as role FROM users u JOIN roles r ON u.role_id = r.id;
SELECT name, entity_type FROM client_entities;
SELECT request_number, status FROM service_requests ORDER BY created_at DESC;
```

---

## Troubleshooting

### Container not starting
```bash
docker-compose -f docker-compose.windows.yml down
docker-compose -f docker-compose.windows.yml up -d --build
```

### Database connection issues
```bash
docker exec crm-db psql -U postgres -c "SELECT 1"
```

### Reset database
```bash
docker-compose -f docker-compose.windows.yml down -v
docker-compose -f docker-compose.windows.yml up -d
docker exec crm-backend python seed_test_data.py
```

### View logs
```bash
docker logs crm-backend -f
docker logs crm-frontend -f
```

---

## Notes

- **2FA is disabled** for all test accounts for easier testing
- All test accounts are **pre-verified**
- **Staff accounts** (admin, senior, accountants) skip onboarding flow
- **Client accounts** will go through onboarding on first login
- Supervisor relationships are automatically set up
- Services use the default workflow with all status steps

---

## Re-seeding Data

To reset and re-seed the demo data:

```bash
# Connect to database and clean up
docker exec crm-db psql -U postgres -d accountant_crm -c "
DELETE FROM job_notes WHERE service_request_id IN (SELECT id FROM service_requests WHERE request_number LIKE 'REQ-0001%');
DELETE FROM queries WHERE service_request_id IN (SELECT id FROM service_requests WHERE request_number LIKE 'REQ-0001%');
DELETE FROM service_requests WHERE request_number LIKE 'REQ-0001%';
DELETE FROM service_requests WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@demo.com');
UPDATE users SET supervisor_id = NULL WHERE supervisor_id IN (SELECT id FROM users WHERE email LIKE '%@demo.com');
DELETE FROM client_entities WHERE name IN ('Bob''s Construction Pty Ltd', 'Bob Smith Family Trust', 'Alice Tech Solutions', 'Alice & Co Holdings', 'Charlie Consulting', 'Smith Family SMSF');
DELETE FROM users WHERE email LIKE '%@demo.com';
DELETE FROM companies WHERE name = 'Demo Accounting Firm';
"

# Re-run seed script
docker exec crm-backend python seed_test_data.py

# Disable 2FA and skip onboarding for staff
docker exec crm-db psql -U postgres -d accountant_crm -c "
UPDATE users SET two_fa_enabled = false WHERE email LIKE '%@demo.com';
UPDATE users SET is_first_login = false WHERE email LIKE '%@demo.com' AND email NOT LIKE 'client%';
"
```
