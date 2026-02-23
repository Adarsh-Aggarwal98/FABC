# Xero Practice Manager Integration

This document describes how to integrate the Accountant CRM with Xero Practice Manager to automatically create jobs when service requests are assigned to accountants.

## Overview

When an admin assigns a service request to an accountant in the CRM, the system will:
1. Create a corresponding job in Xero Practice Manager
2. Store the Xero Job ID in the service request
3. Sync status updates between both systems

---

## Multi-Tenant Architecture (Practice Separation)

**Each practice has their own independent Xero connection.** This ensures complete data isolation between practices.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CRM Platform                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   ABC Accounting    │  │   Smith Tax Co.     │  │   XYZ Partners      │  │
│  │   (Company A)       │  │   (Company B)       │  │   (Company C)       │  │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤  │
│  │ Xero Connection:    │  │ Xero Connection:    │  │ Xero Connection:    │  │
│  │ ✓ Connected         │  │ ✓ Connected         │  │ ✗ Not Connected     │  │
│  │ Tenant: ABC Pty Ltd │  │ Tenant: Smith & Co  │  │                     │  │
│  │                     │  │                     │  │                     │  │
│  │ Mappings:           │  │ Mappings:           │  │ No Xero features    │  │
│  │ - 5 staff mapped    │  │ - 3 staff mapped    │  │ available           │  │
│  │ - 50 clients synced │  │ - 120 clients synced│  │                     │  │
│  │ - 4 services mapped │  │ - 6 services mapped │  │                     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│           │                        │                                         │
│           ▼                        ▼                                         │
└───────────┼────────────────────────┼─────────────────────────────────────────┘
            │                        │
            ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐
│  Xero: ABC Pty Ltd  │  │  Xero: Smith & Co   │
│  (Separate Org)     │  │  (Separate Org)     │
│                     │  │                     │
│  Jobs created here  │  │  Jobs created here  │
│  for ABC clients    │  │  for Smith clients  │
└─────────────────────┘  └─────────────────────┘
```

### Key Isolation Points

| Component | Isolation Level | Description |
|-----------|-----------------|-------------|
| **Xero Connection** | Per Company | Each practice connects their own Xero org |
| **OAuth Tokens** | Per Company | Separate access/refresh tokens per practice |
| **Tenant ID** | Per Company | Each practice's Xero tenant ID stored separately |
| **Contact Mappings** | Per Company | Client-to-Xero-Contact mappings are company-specific |
| **Staff Mappings** | Per Company | Accountant-to-Xero-Staff mappings are company-specific |
| **Service Mappings** | Per Company | Service-to-Job-Template mappings are company-specific |
| **Sync Logs** | Per Company | Each practice sees only their sync history |

### Database Design for Isolation

All Xero-related tables include `company_id` as a foreign key:

```sql
-- Each company has ONE Xero connection
CREATE TABLE xero_connections (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id) UNIQUE,  -- ONE per company
    xero_tenant_id VARCHAR(100) NOT NULL,
    xero_tenant_name VARCHAR(200),
    access_token TEXT NOT NULL,      -- Encrypted, company-specific
    refresh_token TEXT NOT NULL,     -- Encrypted, company-specific
    ...
);

-- Contact mappings are per-company
CREATE TABLE xero_contact_mappings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),  -- Scoped to company
    user_id VARCHAR(36) REFERENCES users(id),
    xero_contact_id VARCHAR(100),
    ...
    UNIQUE(company_id, user_id)  -- Same client can have different Xero contacts per company
);

-- Staff mappings are per-company
CREATE TABLE xero_user_mappings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),  -- Scoped to company
    user_id VARCHAR(36) REFERENCES users(id),
    xero_staff_id VARCHAR(100),
    ...
    UNIQUE(company_id, user_id)
);

-- Service mappings are per-company
CREATE TABLE xero_service_mappings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),  -- Scoped to company
    service_id INTEGER REFERENCES services(id),
    xero_job_template_id VARCHAR(100),
    ...
    UNIQUE(company_id, service_id)
);
```

### Code Implementation for Isolation

```python
class XeroService:
    def __init__(self, company_id):
        """
        Initialize Xero service for a SPECIFIC company.
        All operations are scoped to this company's Xero connection.
        """
        self.company_id = company_id
        self.connection = self._get_connection()

    def _get_connection(self):
        """Get Xero connection for THIS company only."""
        return XeroConnection.query.filter_by(
            company_id=self.company_id,  # Always filter by company
            is_active=True
        ).first()

    def _get_or_create_contact(self, user):
        """Get/create Xero contact scoped to THIS company's Xero org."""
        # Check mapping for THIS company
        mapping = XeroContactMapping.query.filter_by(
            company_id=self.company_id,  # Scoped to company
            user_id=user.id
        ).first()
        ...
```

### User Access Control

| Role | Can Connect Xero | Can View Settings | Can See Other Companies |
|------|-----------------|-------------------|------------------------|
| Super Admin | ✓ Any company | ✓ All companies | ✓ Yes |
| Practice Admin | ✓ Own company only | ✓ Own company only | ✗ No |
| Accountant | ✗ No | ✗ No | ✗ No |
| Client | ✗ No | ✗ No | ✗ No |

### API Endpoint Isolation

All Xero API endpoints validate company access:

```python
@xero_bp.route('/connect', methods=['GET'])
@jwt_required()
@admin_required
def connect_xero():
    """Connect Xero for current user's company."""
    current_user = get_current_user()
    company_id = current_user.company_id  # User's own company only

    # Super admin can specify company_id
    if current_user.role.name == 'super_admin' and request.args.get('company_id'):
        company_id = request.args.get('company_id')

    # Generate OAuth URL with company_id in state
    state = generate_state(company_id)
    return redirect(xero_oauth_url(state))


@xero_bp.route('/status', methods=['GET'])
@jwt_required()
@admin_required
def get_xero_status():
    """Get Xero connection status for user's company."""
    current_user = get_current_user()
    company_id = current_user.company_id

    connection = XeroConnection.query.filter_by(
        company_id=company_id  # Only this company's connection
    ).first()

    return success_response({
        'connected': connection is not None and connection.is_active,
        'tenant_name': connection.xero_tenant_name if connection else None,
        'connected_at': connection.connected_at.isoformat() if connection else None
    })
```

### What Practice Admins See

When Practice Admin of "ABC Accounting" goes to Settings → Integrations → Xero:

```
┌─────────────────────────────────────────────────────────────────┐
│  Xero Integration - ABC Accounting                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Connection Status                                               │
│  ✓ Connected to: ABC Pty Ltd (Xero Organization)                │
│  Connected on: 15 Jan 2025 by John Smith                        │
│                                                                  │
│  [Disconnect]  [Reconnect]                                      │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Staff Mapping (ABC Accounting → Xero)                          │
│  ┌────────────────────┬────────────────────┐                    │
│  │ CRM Accountant     │ Xero Staff Member  │                    │
│  ├────────────────────┼────────────────────┤                    │
│  │ Jane Doe           │ Jane Doe [✓]       │                    │
│  │ Mike Brown         │ Michael Brown [✓]  │                    │
│  │ Sarah Lee          │ [Not Mapped]       │                    │
│  └────────────────────┴────────────────────┘                    │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Service → Job Template Mapping                                  │
│  ┌────────────────────────┬────────────────────────┐            │
│  │ CRM Service            │ Xero Job Template      │            │
│  ├────────────────────────┼────────────────────────┤            │
│  │ Individual Tax Return  │ Tax Return - Individual│            │
│  │ BAS                    │ BAS Preparation        │            │
│  │ Company Tax            │ [Select Template ▼]    │            │
│  └────────────────────────┴────────────────────────┘            │
│                                                                  │
│                                    [Save Mappings]               │
└─────────────────────────────────────────────────────────────────┘
```

They ONLY see their own company's Xero settings - never other companies.

---

## Prerequisites

### 1. Xero Developer Account
- Create an account at https://developer.xero.com/
- Create a new App (OAuth 2.0)

### 2. Required Xero API Scopes
```
openid
profile
email
accounting.transactions
accounting.contacts
payroll.employees
projects
```

### 3. Xero Practice Manager Subscription
- Your Xero organization must have Practice Manager enabled
- API access requires appropriate subscription level

---

## Configuration

### Step 1: Create Xero App

1. Go to https://developer.xero.com/app/manage
2. Click "New App"
3. Fill in:
   - App name: `Accountant CRM`
   - Company URL: Your company website
   - OAuth 2.0 redirect URI: `https://yourdomain.com/api/integrations/xero/callback`
4. Save and note down:
   - Client ID
   - Client Secret

### Step 2: Add Environment Variables

Add these to your `.env` file:

```env
# Xero Integration
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret
XERO_REDIRECT_URI=https://yourdomain.com/api/integrations/xero/callback
XERO_SCOPES=openid profile email accounting.contacts projects
```

### Step 3: Connect Xero Account (Admin)

1. Login as Admin in the CRM
2. Go to Settings → Integrations → Xero
3. Click "Connect to Xero"
4. Authorize the app in Xero
5. Select your Xero organization
6. Save connection

---

## API Endpoints

### Connect Xero Account
```
GET /api/integrations/xero/connect
```
Redirects to Xero OAuth authorization page.

### OAuth Callback
```
GET /api/integrations/xero/callback?code=xxx&state=xxx
```
Handles OAuth callback and stores tokens.

### Disconnect Xero
```
POST /api/integrations/xero/disconnect
```
Removes Xero connection for the company.

### Get Connection Status
```
GET /api/integrations/xero/status
```
Returns current Xero connection status.

### Sync Job to Xero (Manual)
```
POST /api/integrations/xero/sync-job/{request_id}
```
Manually syncs a service request to Xero.

---

## Automatic Job Creation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CRM System                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Admin assigns request to accountant                         │
│     POST /api/requests/{id}/assign                              │
│                                                                  │
│  2. System checks if Xero is connected                          │
│                                                                  │
│  3. If connected, create job in Xero:                           │
│     - Map client to Xero contact                                │
│     - Map service to Xero job template                          │
│     - Set accountant as job manager                             │
│                                                                  │
│  4. Store Xero Job ID in service_requests table                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Xero Practice Manager                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  New Job Created:                                                │
│  - Job Name: "{Service Name} - {Client Name}"                   │
│  - Job Number: Auto-generated by Xero                           │
│  - Client: Linked Xero Contact                                  │
│  - Manager: Accountant (if mapped)                              │
│  - Status: In Progress                                          │
│  - Due Date: From service request                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Changes

Add these columns to `service_requests` table:

```sql
ALTER TABLE service_requests ADD COLUMN xero_job_id VARCHAR(100);
ALTER TABLE service_requests ADD COLUMN xero_job_number VARCHAR(50);
ALTER TABLE service_requests ADD COLUMN xero_synced_at TIMESTAMP;
ALTER TABLE service_requests ADD COLUMN xero_sync_error TEXT;
```

Add Xero connection table:

```sql
CREATE TABLE xero_connections (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),
    xero_tenant_id VARCHAR(100) NOT NULL,
    xero_tenant_name VARCHAR(200),
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,
    connected_by_id VARCHAR(36) REFERENCES users(id),
    connected_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(company_id)
);
```

Add Xero mapping tables:

```sql
-- Map CRM users to Xero staff
CREATE TABLE xero_user_mappings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),
    user_id VARCHAR(36) REFERENCES users(id),
    xero_staff_id VARCHAR(100),
    xero_staff_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, user_id)
);

-- Map CRM clients to Xero contacts
CREATE TABLE xero_contact_mappings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),
    user_id VARCHAR(36) REFERENCES users(id),  -- Client user
    xero_contact_id VARCHAR(100),
    xero_contact_name VARCHAR(200),
    auto_created BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, user_id)
);

-- Map CRM services to Xero job templates
CREATE TABLE xero_service_mappings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),
    service_id INTEGER REFERENCES services(id),
    xero_job_template_id VARCHAR(100),
    xero_job_template_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, service_id)
);
```

---

## Implementation Code

### 1. Xero Service (`backend/app/modules/integrations/xero_service.py`)

```python
import requests
from datetime import datetime, timedelta
from flask import current_app
from app.extensions import db

class XeroService:
    BASE_URL = "https://api.xero.com/api.xro/2.0"
    PROJECTS_URL = "https://api.xero.com/projects.xro/2.0"

    def __init__(self, company_id):
        self.company_id = company_id
        self.connection = self._get_connection()

    def _get_connection(self):
        from app.modules.integrations.models import XeroConnection
        return XeroConnection.query.filter_by(
            company_id=self.company_id,
            is_active=True
        ).first()

    def is_connected(self):
        return self.connection is not None

    def _get_access_token(self):
        """Get valid access token, refreshing if needed."""
        if not self.connection:
            raise Exception("Xero not connected")

        # Refresh token if expired
        if datetime.utcnow() >= self.connection.token_expires_at:
            self._refresh_token()

        return self.connection.access_token

    def _refresh_token(self):
        """Refresh the access token using refresh token."""
        response = requests.post(
            "https://identity.xero.com/connect/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.connection.refresh_token,
                "client_id": current_app.config['XERO_CLIENT_ID'],
                "client_secret": current_app.config['XERO_CLIENT_SECRET'],
            }
        )

        if response.status_code == 200:
            tokens = response.json()
            self.connection.access_token = tokens['access_token']
            self.connection.refresh_token = tokens['refresh_token']
            self.connection.token_expires_at = datetime.utcnow() + timedelta(
                seconds=tokens['expires_in']
            )
            db.session.commit()
        else:
            raise Exception("Failed to refresh Xero token")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Xero-tenant-id": self.connection.xero_tenant_id,
            "Content-Type": "application/json",
        }

    def create_job(self, service_request, client_user, accountant_user, service):
        """
        Create a job in Xero Practice Manager.

        Args:
            service_request: ServiceRequest model instance
            client_user: User model instance (the client)
            accountant_user: User model instance (assigned accountant)
            service: Service model instance

        Returns:
            dict with xero_job_id and xero_job_number
        """
        # Get or create Xero contact for client
        xero_contact_id = self._get_or_create_contact(client_user)

        # Get job template mapping for service (optional)
        template_id = self._get_service_template(service.id)

        # Build job data
        job_data = {
            "contactId": xero_contact_id,
            "name": f"{service.name} - {client_user.full_name}",
            "deadlineUtc": service_request.due_date.isoformat() if service_request.due_date else None,
            "estimateAmount": float(service.base_price) if service.base_price else 0,
        }

        # Add template if mapped
        if template_id:
            job_data["templateId"] = template_id

        # Create job via Projects API
        response = requests.post(
            f"{self.PROJECTS_URL}/projects",
            headers=self._headers(),
            json=job_data
        )

        if response.status_code in [200, 201]:
            job = response.json()
            return {
                "xero_job_id": job["projectId"],
                "xero_job_number": job.get("projectNumber", ""),
            }
        else:
            error = response.json().get("message", response.text)
            raise Exception(f"Failed to create Xero job: {error}")

    def _get_or_create_contact(self, user):
        """Get existing Xero contact or create new one."""
        from app.modules.integrations.models import XeroContactMapping

        # Check existing mapping
        mapping = XeroContactMapping.query.filter_by(
            company_id=self.company_id,
            user_id=user.id
        ).first()

        if mapping:
            return mapping.xero_contact_id

        # Search for existing contact by email
        response = requests.get(
            f"{self.BASE_URL}/Contacts",
            headers=self._headers(),
            params={"where": f'EmailAddress=="{user.email}"'}
        )

        if response.status_code == 200:
            contacts = response.json().get("Contacts", [])
            if contacts:
                contact = contacts[0]
                # Save mapping
                mapping = XeroContactMapping(
                    company_id=self.company_id,
                    user_id=user.id,
                    xero_contact_id=contact["ContactID"],
                    xero_contact_name=contact["Name"],
                    auto_created=False
                )
                db.session.add(mapping)
                db.session.commit()
                return contact["ContactID"]

        # Create new contact
        contact_data = {
            "Contacts": [{
                "Name": user.full_name,
                "FirstName": user.first_name,
                "LastName": user.last_name,
                "EmailAddress": user.email,
                "Phones": [{"PhoneNumber": user.phone}] if user.phone else [],
            }]
        }

        response = requests.post(
            f"{self.BASE_URL}/Contacts",
            headers=self._headers(),
            json=contact_data
        )

        if response.status_code in [200, 201]:
            contact = response.json()["Contacts"][0]
            # Save mapping
            mapping = XeroContactMapping(
                company_id=self.company_id,
                user_id=user.id,
                xero_contact_id=contact["ContactID"],
                xero_contact_name=contact["Name"],
                auto_created=True
            )
            db.session.add(mapping)
            db.session.commit()
            return contact["ContactID"]
        else:
            raise Exception("Failed to create Xero contact")

    def _get_service_template(self, service_id):
        """Get Xero job template ID for a service."""
        from app.modules.integrations.models import XeroServiceMapping

        mapping = XeroServiceMapping.query.filter_by(
            company_id=self.company_id,
            service_id=service_id
        ).first()

        return mapping.xero_job_template_id if mapping else None

    def update_job_status(self, xero_job_id, status):
        """Update job status in Xero."""
        status_map = {
            "completed": "CLOSED",
            "cancelled": "CLOSED",
            "processing": "INPROGRESS",
        }

        xero_status = status_map.get(status)
        if not xero_status:
            return

        response = requests.patch(
            f"{self.PROJECTS_URL}/projects/{xero_job_id}",
            headers=self._headers(),
            json={"status": xero_status}
        )

        return response.status_code in [200, 204]
```

### 2. Update Request Assignment Logic

In `backend/app/modules/services/usecases.py`, update the assign method:

```python
def assign_request(self, request_id, accountant_id, current_user):
    """Assign request to accountant and create Xero job if connected."""
    from app.modules.integrations.xero_service import XeroService

    request = self.request_repo.find_by_id(request_id)
    if not request:
        raise ValueError("Request not found")

    accountant = self.user_repo.find_by_id(accountant_id)
    if not accountant:
        raise ValueError("Accountant not found")

    # Assign in CRM
    request.assigned_to_id = accountant_id
    request.status = ServiceRequest.STATUS_ASSIGNED
    request.assigned_at = datetime.utcnow()

    # Create Xero job if connected
    xero_service = XeroService(request.company_id)
    if xero_service.is_connected():
        try:
            client = self.user_repo.find_by_id(request.user_id)
            service = request.service

            xero_result = xero_service.create_job(
                service_request=request,
                client_user=client,
                accountant_user=accountant,
                service=service
            )

            request.xero_job_id = xero_result["xero_job_id"]
            request.xero_job_number = xero_result["xero_job_number"]
            request.xero_synced_at = datetime.utcnow()
            request.xero_sync_error = None

        except Exception as e:
            # Log error but don't fail assignment
            request.xero_sync_error = str(e)
            current_app.logger.error(f"Xero sync failed: {e}")

    db.session.commit()
    return request
```

---

## Admin UI for Xero Settings

### Settings Page Features

1. **Connection Status**
   - Show connected organization name
   - Connection date and connected by
   - Disconnect button

2. **Staff Mapping**
   - Map CRM accountants to Xero staff members
   - Auto-suggest based on email match

3. **Client Sync Settings**
   - Auto-create contacts in Xero (on/off)
   - Sync client details on update

4. **Service Mapping**
   - Map CRM services to Xero job templates
   - Set default job category

5. **Sync Logs**
   - View recent sync activities
   - Error log with retry option

---

## Webhook Support (Optional)

To receive updates from Xero when jobs are modified:

### Register Webhook
```
POST https://api.xero.com/webhooks
{
  "webhookKey": "your-webhook-key",
  "webhookUrl": "https://yourdomain.com/api/integrations/xero/webhook"
}
```

### Webhook Events
- `project.status.changed` - Job status updated
- `project.completed` - Job marked complete
- `invoice.created` - Invoice created for job

---

## Testing the Integration

### 1. Test Connection
```bash
# After connecting Xero in admin settings
curl -X GET http://localhost:5000/api/integrations/xero/status \
  -H "Authorization: Bearer {admin_token}"
```

### 2. Test Job Creation
```bash
# Assign a request (should create Xero job)
curl -X POST http://localhost:5000/api/requests/{request_id}/assign \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"accountant_id": "{accountant_user_id}"}'
```

### 3. Verify in Xero
1. Login to Xero Practice Manager
2. Go to Jobs/Projects
3. Verify new job created with correct details

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Token expired` | Access token expired | Auto-refresh using refresh token |
| `Invalid tenant` | Wrong organization selected | Re-connect Xero account |
| `Contact not found` | Client not in Xero | Auto-create contact |
| `Rate limited` | Too many API calls | Implement retry with backoff |
| `Insufficient permissions` | Missing API scopes | Re-authorize with correct scopes |

---

## Rate Limits

Xero API limits:
- 60 calls per minute per tenant
- 5000 calls per day per tenant

Implement:
- Request queuing for bulk operations
- Exponential backoff on 429 errors
- Daily sync batching for large data

---

## Security Considerations

1. **Token Storage**: Encrypt access/refresh tokens at rest
2. **Scope Minimization**: Only request necessary scopes
3. **Audit Logging**: Log all Xero API calls
4. **Token Rotation**: Refresh tokens regularly
5. **Webhook Validation**: Verify Xero webhook signatures

---

## Future Enhancements

1. **Time Tracking Sync**: Sync time entries from Xero to CRM
2. **Invoice Sync**: Create CRM invoices from Xero invoices
3. **Two-way Status Sync**: Update CRM when Xero job status changes
4. **Bulk Sync**: Initial sync of existing clients/jobs
5. **Multi-org Support**: Connect multiple Xero organizations

---

## Support

For issues with Xero integration:
- Xero API Documentation: https://developer.xero.com/documentation/
- Xero Developer Community: https://community.xero.com/developer
- CRM Support: Create issue on GitHub
