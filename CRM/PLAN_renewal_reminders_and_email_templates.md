# Plan: Service Renewal Reminders & Service-Based Email Templates

## Overview
Enable practice owners to:
1. Send automatic reminder emails for recurring services (like ITR, BAS, etc.)
2. Associate email templates with specific services
3. Configure renewal periods and reminder schedules

---

## Part 1: Service Renewal Reminder System

### Problem
When a client completes a service like ITR (Income Tax Return), the practice wants to automatically remind them next year when it's time to file again.

### Solution Design

#### 1.1 Add Renewal Fields to Service Model

**File:** `backend/app/modules/services/models.py`

Add to `Service` model:
```python
# Renewal configuration
is_recurring = db.Column(db.Boolean, default=False)  # Is this a recurring service?
renewal_period_months = db.Column(db.Integer, default=12)  # How often to renew (12 = yearly, 3 = quarterly)
renewal_reminder_days = db.Column(db.JSON, default=list)  # Days before due date to send reminders [30, 14, 7]
renewal_due_month = db.Column(db.Integer)  # Fixed due month (e.g., 10 for October for ITR)
renewal_due_day = db.Column(db.Integer)  # Fixed due day (e.g., 31 for Oct 31)
```

**Example Service Configurations:**
| Service | renewal_period_months | renewal_due_month | renewal_due_day | reminder_days |
|---------|----------------------|-------------------|-----------------|---------------|
| Individual Tax Return | 12 | 10 | 31 | [60, 30, 14, 7] |
| BAS (Monthly) | 1 | null | 21 | [7, 3] |
| BAS (Quarterly) | 3 | null | 28 | [14, 7, 3] |
| SMSF Audit | 12 | 2 | 28 | [60, 30, 14] |

#### 1.2 Create Service Renewal Tracking Table

**File:** `backend/migrations/add_service_renewals.sql`

```sql
CREATE TABLE service_renewals (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    company_id VARCHAR(36) NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

    -- Last completion
    last_completed_at TIMESTAMP,
    last_request_id VARCHAR(36) REFERENCES service_requests(id),

    -- Next renewal
    next_due_date DATE NOT NULL,

    -- Reminder tracking
    reminders_sent JSONB DEFAULT '[]',  -- [{sent_at, days_before, email_id}]
    last_reminder_at TIMESTAMP,

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reminded, completed, skipped
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, service_id, next_due_date)
);

CREATE INDEX idx_renewals_due_date ON service_renewals(next_due_date);
CREATE INDEX idx_renewals_user ON service_renewals(user_id);
CREATE INDEX idx_renewals_status ON service_renewals(status);
```

#### 1.3 Backend: Renewal Service

**File:** `backend/app/modules/services/renewal_service.py`

```python
class RenewalService:
    @staticmethod
    def calculate_next_due_date(service, from_date=None):
        """Calculate next due date based on service renewal config"""

    @staticmethod
    def create_renewal_record(user_id, service_id, completed_request_id):
        """Called when a service request is marked completed"""

    @staticmethod
    def get_due_reminders():
        """Get all renewals that need reminders sent today"""

    @staticmethod
    def send_renewal_reminder(renewal, days_before):
        """Send reminder email for a renewal"""

    @staticmethod
    def process_daily_reminders():
        """Daily job to send all due reminders"""
```

#### 1.4 Trigger: Create Renewal on Service Completion

When a ServiceRequest status changes to `completed`:
1. Check if the service `is_recurring = True`
2. Create or update `ServiceRenewal` record for this user+service
3. Calculate `next_due_date` based on service config

**File:** `backend/app/modules/services/usecases.py` - Update status change handler

#### 1.5 Daily Scheduler Job

**File:** `backend/app/jobs/renewal_reminders.py`

```python
def run_daily_renewal_check():
    """
    Run daily at 8 AM (configurable per company timezone)
    1. Get all renewals where next_due_date - today <= max(reminder_days)
    2. For each, check which reminders haven't been sent yet
    3. Send appropriate reminder emails
    4. Log sent reminders
    """
```

**Trigger Options:**
- Celery Beat (recommended for production)
- APScheduler (simpler for small deployments)
- External cron job hitting an API endpoint

#### 1.6 Default Renewal Configurations for Services

**Migration:** Seed default renewal settings for existing services

| Category | Service | Period | Due Month | Due Day | Reminders |
|----------|---------|--------|-----------|---------|-----------|
| tax_agent | Individual Tax Return | 12 | 10 | 31 | [60,30,14,7] |
| tax_agent | Company Tax Return | 12 | 2 | 28 | [60,30,14] |
| bas_agent | BAS Lodgement (Monthly) | 1 | - | 21 | [7,3] |
| bas_agent | BAS Lodgement (Quarterly) | 3 | - | 28 | [14,7,3] |
| auditor | SMSF Audit | 12 | 2 | 28 | [60,30,14] |
| bookkeeper | Monthly Bookkeeping | 1 | - | 5 | [3] |

---

## Part 2: Service-Based Email Templates

### Problem
The email templates page shows all templates but users can't:
1. See which templates are for which service
2. Create service-specific templates (e.g., "ITR Reminder" vs "BAS Reminder")

### Solution Design

#### 2.1 Add Service Link to Email Template

**File:** `backend/app/modules/notifications/models.py`

Add to `EmailTemplate` model:
```python
# Service association (optional - NULL means general template)
service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)

# Template type for categorization
template_type = db.Column(db.String(50))  # 'welcome', 'invoice', 'reminder', 'query', 'completion', 'renewal'
```

#### 2.2 Migration for Service Templates

```sql
-- Add service_id to email_templates
ALTER TABLE email_templates ADD COLUMN service_id INTEGER REFERENCES services(id);
ALTER TABLE email_templates ADD COLUMN template_type VARCHAR(50);

-- Create default renewal reminder templates
INSERT INTO email_templates (name, slug, subject, body_html, template_type, variables)
VALUES
('Service Renewal Reminder', 'renewal_reminder',
 '{service_name} - Time to Renew for {due_year}',
 '<p>Dear {client_name},</p><p>This is a friendly reminder that your <strong>{service_name}</strong> is due by <strong>{due_date}</strong>.</p><p>Please contact us to get started.</p>',
 'renewal', '["client_name", "service_name", "due_date", "due_year", "company_name"]');
```

#### 2.3 Update Email Templates API

**File:** `backend/app/modules/notifications/routes.py`

- Add `service_id` filter to list endpoint
- Allow creating service-specific templates
- Return service info in template response

#### 2.4 Update Email Templates Frontend

**File:** `frontend/src/pages/settings/EmailTemplates.jsx`

Changes:
1. Add service dropdown filter
2. Show service badge on templates
3. Add service selector when creating/editing template
4. Group templates by type (Welcome, Invoice, Reminder, etc.)

```jsx
// Add filter state
const [filterService, setFilterService] = useState('all');
const [services, setServices] = useState([]);

// Filter templates
const filteredTemplates = templates.filter(t =>
  filterService === 'all' || t.service_id === filterService
);

// Add to form
<Select
  label="Associated Service (Optional)"
  value={formData.service_id}
  onChange={(e) => handleChange('service_id', e.target.value)}
  options={[
    { value: '', label: 'General (All Services)' },
    ...services.map(s => ({ value: s.id, label: s.name }))
  ]}
/>
```

---

## Part 3: Admin UI for Renewal Configuration

### 3.1 Service Edit Form - Add Renewal Tab

**File:** `frontend/src/pages/services/ServiceForm.jsx` or `ServiceList.jsx`

When editing a service, add a "Renewal Settings" section:

```
[ ] This is a recurring service

If recurring:
- Renewal Period: [12] months (or dropdown: Monthly, Quarterly, Yearly, Custom)
- Due Date:
  [ ] Fixed date each year: Month [October] Day [31]
  [ ] Days after completion: [365] days
- Reminder Schedule:
  [x] 60 days before
  [x] 30 days before
  [x] 14 days before
  [x] 7 days before
  [ ] Custom: [___] days before
```

### 3.2 Renewal Dashboard

**File:** `frontend/src/pages/settings/RenewalsDashboard.jsx`

Show upcoming renewals:
- List of clients with services due in next 30/60/90 days
- Filter by service type
- Manual "Send Reminder" button
- "Mark as Completed" or "Skip This Year" options
- Bulk actions

---

## Implementation Phases

### Phase 1: Database & Models
1. Add renewal fields to Service model
2. Create service_renewals table
3. Add service_id to email_templates
4. Create migrations

### Phase 2: Backend Logic
1. Create RenewalService with calculation logic
2. Update service completion to create renewal records
3. Create reminder sending logic
4. Add API endpoints for renewal management

### Phase 3: Scheduler
1. Set up APScheduler or Celery Beat
2. Create daily renewal check job
3. Configure timezone-aware scheduling

### Phase 4: Frontend - Email Templates
1. Add service filter to templates page
2. Add service selector to template form
3. Create default renewal template

### Phase 5: Frontend - Service Renewal Config
1. Add renewal settings to service edit form
2. Create renewals dashboard
3. Add manual reminder controls

### Phase 6: Testing & Seeding
1. Seed default renewal configs for services
2. Create renewal reminder template
3. Test end-to-end flow

---

## Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `backend/app/modules/services/renewal_service.py` | Renewal calculation and reminder logic |
| `backend/app/jobs/renewal_reminders.py` | Daily scheduler job |
| `backend/migrations/add_service_renewals.sql` | Database migration |
| `frontend/src/pages/settings/RenewalsDashboard.jsx` | Admin renewals view |

### Modified Files
| File | Changes |
|------|---------|
| `backend/app/modules/services/models.py` | Add renewal fields to Service, create ServiceRenewal model |
| `backend/app/modules/notifications/models.py` | Add service_id to EmailTemplate |
| `backend/app/modules/services/usecases.py` | Trigger renewal creation on completion |
| `backend/app/modules/services/routes.py` | Add renewal management endpoints |
| `backend/app/modules/notifications/routes.py` | Add service filter to templates |
| `frontend/src/pages/settings/EmailTemplates.jsx` | Add service filter and selector |
| `frontend/src/pages/services/ServiceList.jsx` | Add renewal config UI |

---

## Example Flow

1. **Setup:** Admin configures ITR service with:
   - `is_recurring = True`
   - `renewal_period_months = 12`
   - `renewal_due_month = 10, renewal_due_day = 31`
   - `reminder_days = [60, 30, 14, 7]`

2. **Client Completes ITR:**
   - ServiceRequest marked `completed` on Jan 15, 2024
   - System creates ServiceRenewal:
     - `next_due_date = Oct 31, 2024`
     - `status = pending`

3. **Reminder Schedule:**
   - Aug 31, 2024 (60 days before): First reminder sent
   - Oct 1, 2024 (30 days before): Second reminder
   - Oct 17, 2024 (14 days before): Third reminder
   - Oct 24, 2024 (7 days before): Final reminder

4. **Client Requests Service:**
   - Client clicks link in reminder email
   - Creates new ServiceRequest for ITR
   - Renewal status updated to `completed`
   - New renewal created for Oct 31, 2025

---

## Verification Checklist

- [ ] Service model has renewal fields
- [ ] ServiceRenewal table created
- [ ] Completion triggers renewal creation
- [ ] Daily job identifies due reminders
- [ ] Reminder emails sent with correct template
- [ ] Admin can configure renewal settings per service
- [ ] Email templates can be filtered by service
- [ ] Renewals dashboard shows upcoming renewals
- [ ] Manual reminder sending works
