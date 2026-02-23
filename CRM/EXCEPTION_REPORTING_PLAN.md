# Exception Reporting Plan for CRM

## Overview
Exception reporting helps identify discrepancies, bottlenecks, and areas requiring attention in the accounting practice workflow.

## Requested Exception Reports

### 1. Clients Without Jobs
**Purpose:** Identify clients who have been onboarded but have no service requests created.

**Query Logic:**
```sql
SELECT u.id, u.first_name, u.last_name, u.email, u.created_at
FROM users u
LEFT JOIN service_requests sr ON u.id = sr.user_id
WHERE u.role_id = 4  -- Client role
AND u.company_id = :company_id
AND sr.id IS NULL
ORDER BY u.created_at DESC;
```

**API Endpoint:** `GET /api/analytics/exceptions/clients-without-jobs`

---

### 2. Jobs Created vs Jobs in WIP
**Purpose:** Compare total jobs created vs jobs currently in progress (Work in Progress).

**Query Logic:**
```sql
SELECT
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE status = 'in_progress') as jobs_in_wip,
    COUNT(*) FILTER (WHERE status = 'pending') as jobs_pending,
    COUNT(*) FILTER (WHERE status = 'completed') as jobs_completed,
    ROUND(COUNT(*) FILTER (WHERE status = 'in_progress')::decimal / NULLIF(COUNT(*), 0) * 100, 2) as wip_percentage
FROM service_requests sr
JOIN users u ON sr.user_id = u.id
WHERE u.company_id = :company_id;
```

**API Endpoint:** `GET /api/analytics/exceptions/job-status-summary`

---

### 3. Job Creation vs Closure Dates (Turnaround Analysis)
**Purpose:** Analyze job turnaround time - time between creation and completion.

**Query Logic:**
```sql
SELECT
    sr.id,
    s.name as service_name,
    u.first_name || ' ' || u.last_name as client_name,
    sr.created_at as job_created,
    sr.completed_at as job_closed,
    EXTRACT(DAY FROM (sr.completed_at - sr.created_at)) as days_to_complete,
    sr.status
FROM service_requests sr
JOIN services s ON sr.service_id = s.id
JOIN users u ON sr.user_id = u.id
WHERE u.company_id = :company_id
AND sr.status = 'completed'
ORDER BY days_to_complete DESC;
```

**Aggregated View:**
```sql
SELECT
    s.name as service_type,
    COUNT(*) as completed_jobs,
    AVG(EXTRACT(DAY FROM (sr.completed_at - sr.created_at))) as avg_days,
    MIN(EXTRACT(DAY FROM (sr.completed_at - sr.created_at))) as min_days,
    MAX(EXTRACT(DAY FROM (sr.completed_at - sr.created_at))) as max_days
FROM service_requests sr
JOIN services s ON sr.service_id = s.id
JOIN users u ON sr.user_id = u.id
WHERE u.company_id = :company_id
AND sr.status = 'completed'
AND sr.completed_at IS NOT NULL
GROUP BY s.name;
```

**API Endpoint:** `GET /api/analytics/exceptions/job-turnaround`

---

### 4. Jobs Closed vs Invoices Raised vs Invoices Unpaid
**Purpose:** Track billing status for completed jobs.

**Query Logic:**
```sql
SELECT
    COUNT(*) FILTER (WHERE status = 'completed') as jobs_closed,
    COUNT(*) FILTER (WHERE status = 'completed' AND invoice_raised = true) as invoices_raised,
    COUNT(*) FILTER (WHERE status = 'completed' AND invoice_raised = true AND invoice_paid = false) as invoices_unpaid,
    COUNT(*) FILTER (WHERE status = 'completed' AND invoice_raised = true AND invoice_paid = true) as invoices_paid,
    COUNT(*) FILTER (WHERE status = 'completed' AND (invoice_raised = false OR invoice_raised IS NULL)) as not_invoiced,
    SUM(CASE WHEN status = 'completed' AND invoice_raised = true AND invoice_paid = false THEN invoice_amount ELSE 0 END) as unpaid_amount
FROM service_requests sr
JOIN users u ON sr.user_id = u.id
WHERE u.company_id = :company_id;
```

**Detailed Unpaid Invoices:**
```sql
SELECT
    sr.id,
    s.name as service_name,
    u.first_name || ' ' || u.last_name as client_name,
    u.email,
    sr.invoice_amount,
    sr.completed_at,
    sr.created_at
FROM service_requests sr
JOIN services s ON sr.service_id = s.id
JOIN users u ON sr.user_id = u.id
WHERE u.company_id = :company_id
AND sr.status = 'completed'
AND sr.invoice_raised = true
AND (sr.invoice_paid = false OR sr.invoice_paid IS NULL)
ORDER BY sr.completed_at ASC;
```

**API Endpoint:** `GET /api/analytics/exceptions/billing-status`

---

### 5. Leads Not Converted as Clients
**Purpose:** Track potential clients who haven't been fully onboarded.

**Implementation Options:**

#### Option A: Use existing user flags
Track users who started but didn't complete onboarding:
```sql
SELECT u.id, u.email, u.first_name, u.last_name, u.created_at
FROM users u
WHERE u.company_id = :company_id
AND u.role_id = 4
AND u.is_first_login = true  -- Never completed onboarding
ORDER BY u.created_at DESC;
```

#### Option B: Create dedicated Leads table (Recommended)
```sql
CREATE TABLE leads (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(20),
    source VARCHAR(100),  -- referral, website, etc.
    status VARCHAR(50) DEFAULT 'new',  -- new, contacted, qualified, converted, lost
    notes TEXT,
    converted_user_id VARCHAR(36) REFERENCES users(id),
    converted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoint:** `GET /api/analytics/exceptions/unconverted-leads`

---

## Implementation Priority

1. **High Priority** (Immediate value):
   - Jobs Closed vs Invoices (Revenue tracking)
   - Jobs in WIP (Workload management)

2. **Medium Priority**:
   - Clients Without Jobs (Client engagement)
   - Job Turnaround (Performance metrics)

3. **Lower Priority** (Requires new feature):
   - Leads Not Converted (Requires leads management)

---

## Dashboard Integration

Add a new "Exception Reports" section to the Analytics dashboard with:

1. **Summary Cards:**
   - Clients without jobs (count + list link)
   - Jobs in WIP (count + percentage)
   - Unpaid invoices (count + total amount)
   - Overdue jobs (based on expected completion date)

2. **Drill-down Tables:**
   - Click on any card to see detailed list
   - Export to CSV/Excel functionality

3. **Alerts/Notifications:**
   - Email alerts for invoices unpaid > 30 days
   - Weekly summary of exception items

---

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analytics/exceptions/clients-without-jobs` | GET | Clients with no service requests |
| `/api/analytics/exceptions/job-status-summary` | GET | Jobs by status breakdown |
| `/api/analytics/exceptions/job-turnaround` | GET | Job completion time analysis |
| `/api/analytics/exceptions/billing-status` | GET | Invoice and payment tracking |
| `/api/analytics/exceptions/unconverted-leads` | GET | Leads not converted to clients |
| `/api/analytics/exceptions/summary` | GET | All exception metrics combined |

---

## Next Steps

1. Create backend API endpoints for exception reports
2. Add exception reports to analytics dashboard
3. Implement CSV/Excel export for reports
4. Add email notification system for critical exceptions
5. Consider creating Leads management module
