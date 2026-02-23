o# Feature Enhancement Roadmap

## Overview

This document outlines recommended feature enhancements for the Accountant CRM system, focusing on empowering **Practice Owners** (accountants) with greater customization capabilities while maintaining **SuperAdmin** oversight and control.

---

## Table of Contents

1. [Practice Owner Customization Features](#1-practice-owner-customization-features)
2. [Email Template System Enhancements](#2-email-template-system-enhancements)
3. [SuperAdmin Request Management](#3-superadmin-request-management)
4. [Client Management Enhancements](#4-client-management-enhancements)
5. [Billing & Invoice Features](#5-billing--invoice-features)
6. [Communication & Notification Features](#6-communication--notification-features)
7. [Reporting & Analytics](#7-reporting--analytics)
8. [Document Management](#8-document-management)
9. [Calendar & Scheduling](#9-calendar--scheduling)
10. [Compliance & Audit](#10-compliance--audit)
11. [Integration Features](#11-integration-features)
12. [Implementation Priority Matrix](#12-implementation-priority-matrix)

---

## 1. Practice Owner Customization Features

### 1.1 Tenant-Specific Service Catalog

**Current State:** Services are system-wide, managed only by SuperAdmin.

**Enhancement:**
- Allow Practice Owners to create **custom services** specific to their practice
- Inherit system services with ability to override pricing
- Custom service categories per practice

**Database Changes:**
```python
class Service:
    # Add fields:
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    # NULL = system service, otherwise company-specific
    parent_service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    # For overriding system services
    is_system = db.Column(db.Boolean, default=False)
```

**API Endpoints:**
```
POST   /api/services                    # Create custom service (Admin)
PATCH  /api/services/<id>               # Update own service
DELETE /api/services/<id>               # Delete custom service
GET    /api/services?include_system=true # List all available services
```

---

### 1.2 Custom Form Builder for Practice Owners

**Current State:** Only SuperAdmin can create forms.

**Enhancement:**
- Practice Owners can create forms for their practice
- Clone system forms as templates
- Custom intake forms, onboarding questionnaires

**Database Changes:**
```python
class Form:
    # Add fields:
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    is_system = db.Column(db.Boolean, default=False)
    cloned_from_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=True)
```

**Features:**
- Form templates library (system forms)
- Clone & customize functionality
- Form versioning (track changes)
- Draft/Published states

---

### 1.3 Practice Branding & White-Label Options

**Current State:** Limited to logo and primary color.

**Enhancement:**

| Feature | Description |
|---------|-------------|
| **Full Color Scheme** | Primary, secondary, accent colors |
| **Custom Fonts** | Select from web-safe fonts |
| **Custom Domain** | practice.accountantcrm.com or custom domain |
| **Email Branding** | Custom email headers/footers |
| **Login Page** | Branded login experience |
| **Client Portal Theme** | Custom look for client-facing pages |

**Database Changes:**
```python
class CompanyBranding(db.Model):
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    primary_color = db.Column(db.String(7))
    secondary_color = db.Column(db.String(7))
    accent_color = db.Column(db.String(7))
    font_family = db.Column(db.String(100))
    logo_url = db.Column(db.String(500))
    favicon_url = db.Column(db.String(500))
    custom_domain = db.Column(db.String(255))
    email_header_html = db.Column(db.Text)
    email_footer_html = db.Column(db.Text)
    login_banner_url = db.Column(db.String(500))
    tagline = db.Column(db.String(255))
```

---

### 1.4 Custom Client Fields

**Current State:** Fixed user fields only.

**Enhancement:**
- Practice Owners define additional fields for their clients
- Custom dropdown options (e.g., client categories)
- Field visibility controls

**Database Changes:**
```python
class CustomField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    field_name = db.Column(db.String(100))
    field_type = db.Column(db.String(50))  # text, number, date, select, etc.
    options = db.Column(db.JSON)  # For select/multiselect
    is_required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer)
    is_visible_to_client = db.Column(db.Boolean, default=False)

class CustomFieldValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom_field_id = db.Column(db.Integer, db.ForeignKey('custom_fields.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    value = db.Column(db.Text)
```

---

### 1.5 Practice Settings Dashboard

**New Feature:** Centralized settings management for Practice Owners.

**Settings Categories:**
```
Practice Settings
├── General
│   ├── Practice Details
│   ├── Business Hours
│   ├── Time Zone
│   └── Financial Year Settings
├── Branding
│   ├── Logo & Colors
│   ├── Email Templates
│   └── Client Portal Theme
├── Services
│   ├── Service Catalog
│   ├── Pricing
│   └── Service Categories
├── Users & Permissions
│   ├── Team Members
│   ├── Role Permissions
│   └── Client Access Settings
├── Notifications
│   ├── Email Settings
│   ├── Reminder Defaults
│   └── Alert Preferences
├── Integrations
│   ├── Connected Apps
│   ├── API Keys
│   └── Webhooks
└── Billing
    ├── Subscription Plan
    ├── Payment Methods
    └── Invoice Settings
```

---

### 1.6 Custom Workflow States

**Current State:** Fixed status workflow for all practices.

**Enhancement:**
- Practice Owners can define custom statuses
- Custom workflow transitions
- Status-based automation triggers

**Database Changes:**
```python
class CustomStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    name = db.Column(db.String(50))
    color = db.Column(db.String(7))
    order = db.Column(db.Integer)
    is_initial = db.Column(db.Boolean, default=False)
    is_final = db.Column(db.Boolean, default=False)

class StatusTransition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    from_status_id = db.Column(db.Integer, db.ForeignKey('custom_statuses.id'))
    to_status_id = db.Column(db.Integer, db.ForeignKey('custom_statuses.id'))
    allowed_roles = db.Column(db.JSON)  # ['admin', 'accountant']
```

---

## 2. Email Template System Enhancements

### 2.1 Extended Email Template Library

**Current Templates:**
- document_request
- lodgement_confirmation
- payment_reminder
- annual_reminder
- birthday
- welcome
- assignment_notification

**Additional Templates to Add:**

| Template Slug | Purpose | Variables |
|---------------|---------|-----------|
| `quote_sent` | Service quotation | {client_name}, {service_name}, {quote_amount}, {valid_until} |
| `invoice_sent` | Invoice notification | {client_name}, {invoice_number}, {amount}, {due_date}, {payment_link} |
| `invoice_overdue` | Overdue payment | {client_name}, {invoice_number}, {amount}, {days_overdue} |
| `payment_received` | Payment confirmation | {client_name}, {amount}, {payment_date}, {receipt_number} |
| `document_received` | Document acknowledgment | {client_name}, {document_name}, {uploaded_by} |
| `task_completed` | Service completion | {client_name}, {service_name}, {completed_by}, {completion_date} |
| `review_request` | Request client review | {client_name}, {service_name}, {review_link} |
| `bas_reminder` | BAS due reminder | {client_name}, {period}, {due_date} |
| `tax_deadline` | Tax deadline reminder | {client_name}, {tax_year}, {deadline_date} |
| `eofy_reminder` | End of financial year | {client_name}, {financial_year}, {checklist_link} |
| `client_inactive` | Re-engagement email | {client_name}, {last_activity_date}, {days_inactive} |
| `referral_request` | Request referrals | {client_name}, {referral_link} |
| `appointment_reminder` | Meeting reminder | {client_name}, {appointment_date}, {appointment_time}, {meeting_link} |
| `appointment_confirmation` | Booking confirmation | {client_name}, {service_name}, {date}, {time} |
| `password_reset` | Password reset link | {user_name}, {reset_link}, {expiry_time} |
| `two_factor_code` | 2FA OTP email | {user_name}, {otp_code}, {expiry_minutes} |
| `account_locked` | Security notification | {user_name}, {locked_reason}, {unlock_instructions} |
| `new_message` | Query notification | {client_name}, {sender_name}, {message_preview} |
| `monthly_summary` | Monthly activity report | {client_name}, {month}, {completed_tasks}, {pending_tasks} |

---

### 2.2 Email Template Builder UI

**Features:**
- **Visual Editor:** WYSIWYG editor with drag-and-drop blocks
- **Variable Picker:** Insert variables with autocomplete
- **Preview Mode:** See rendered email with sample data
- **Mobile Preview:** Check responsive design
- **Test Send:** Send test email to self

**Template Components:**
```
Header Block
├── Logo
├── Practice Name
└── Custom Banner

Content Blocks
├── Text Block
├── Button Block
├── Image Block
├── Divider
├── Table Block
└── List Block

Footer Block
├── Contact Info
├── Social Links
├── Unsubscribe Link
└── Legal Text
```

---

### 2.3 Email Automation Triggers

**Automated Email Events:**

| Trigger | Template | Timing |
|---------|----------|--------|
| New client registered | `welcome` | Immediate |
| Request submitted | `request_received` | Immediate |
| Request assigned | `assignment_notification` | Immediate |
| Query raised | `new_message` | Immediate |
| Invoice created | `invoice_sent` | Immediate |
| Invoice overdue | `invoice_overdue` | 1, 7, 14 days after due |
| Payment received | `payment_received` | Immediate |
| Task completed | `task_completed` | Immediate |
| BAS due | `bas_reminder` | 14, 7, 3 days before |
| Tax deadline | `tax_deadline` | 30, 14, 7 days before |
| Client birthday | `birthday` | On birthday |
| Client inactive | `client_inactive` | After 90 days |

**Configuration Model:**
```python
class EmailAutomation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    trigger_event = db.Column(db.String(50))
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))
    is_enabled = db.Column(db.Boolean, default=True)
    delay_minutes = db.Column(db.Integer, default=0)
    conditions = db.Column(db.JSON)  # Optional conditions
```

---

### 2.4 Email Analytics

**Track:**
- Emails sent count
- Open rate (requires tracking pixel)
- Click rate (link tracking)
- Bounce rate
- Unsubscribe rate

**Database Model:**
```python
class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_email = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    sent_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    bounced = db.Column(db.Boolean, default=False)
    bounce_reason = db.Column(db.String(255))
```

---

## 3. SuperAdmin Request Management

### 3.1 Practice Onboarding Workflow

**New Feature:** Structured process for new practice registration.

**Workflow:**
```
Practice Owner Signup Request
        ↓
SuperAdmin Review Queue
        ↓
Verify Business Details
        ↓
Select Plan & Set Limits
        ↓
Create Company Record
        ↓
Send Owner Invitation
        ↓
Owner Completes Setup
        ↓
Practice Goes Live
```

**Database Model:**
```python
class PracticeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Requestor Info
    owner_name = db.Column(db.String(100))
    owner_email = db.Column(db.String(255))
    owner_phone = db.Column(db.String(20))

    # Practice Info
    practice_name = db.Column(db.String(200))
    trading_name = db.Column(db.String(200))
    abn = db.Column(db.String(14))
    address = db.Column(db.Text)
    website = db.Column(db.String(255))

    # Business Details
    estimated_clients = db.Column(db.Integer)
    estimated_users = db.Column(db.Integer)
    services_interested = db.Column(db.JSON)

    # Status
    status = db.Column(db.String(20))  # pending, approved, rejected, more_info
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

**API Endpoints:**
```
POST   /api/practice-requests              # Submit new request (public)
GET    /api/practice-requests              # List all requests (SuperAdmin)
GET    /api/practice-requests/<id>         # Get request details
PATCH  /api/practice-requests/<id>/approve # Approve and create company
PATCH  /api/practice-requests/<id>/reject  # Reject with reason
PATCH  /api/practice-requests/<id>/request-info # Request more information
```

---

### 3.2 Practice Owner Invitation System

**New Feature:** SuperAdmin can directly invite and onboard Practice Owners.

**Capabilities:**
- Send invitation email to new practice owners
- Pre-configure company settings before owner accepts
- Set initial plan and limits
- Track invitation status

**Invitation Workflow:**
```
SuperAdmin Creates Invitation
        ↓
Enter Practice & Owner Details
        ↓
Configure Plan & Limits
        ↓
Send Invitation Email
        ↓
Owner Receives Email with Setup Link
        ↓
Owner Creates Password & Accepts Terms
        ↓
Owner Completes Profile Setup
        ↓
Practice Activated
```

**Database Model:**
```python
class PracticeInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Owner Details
    owner_email = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    owner_phone = db.Column(db.String(20))

    # Practice Details (Pre-configured by SuperAdmin)
    practice_name = db.Column(db.String(200), nullable=False)
    trading_name = db.Column(db.String(200))
    abn = db.Column(db.String(14))

    # Plan Configuration
    plan_type = db.Column(db.String(20), default='standard')
    max_users = db.Column(db.Integer, default=5)
    max_clients = db.Column(db.Integer, default=100)

    # Invitation Status
    status = db.Column(db.String(20), default='pending')
    # pending, sent, accepted, expired, cancelled

    invitation_token = db.Column(db.String(255), unique=True)
    token_expires_at = db.Column(db.DateTime)

    # Tracking
    invited_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sent_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)
    reminder_sent_count = db.Column(db.Integer, default=0)
    last_reminder_at = db.Column(db.DateTime)

    # Result
    created_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**API Endpoints:**
```
POST   /api/practice-invitations              # Create & send invitation (SuperAdmin)
GET    /api/practice-invitations              # List all invitations (SuperAdmin)
GET    /api/practice-invitations/<id>         # Get invitation details
PATCH  /api/practice-invitations/<id>/resend  # Resend invitation email
PATCH  /api/practice-invitations/<id>/cancel  # Cancel pending invitation
GET    /api/practice-invitations/accept/<token> # Validate invitation token (Public)
POST   /api/practice-invitations/accept/<token> # Accept invitation & create account (Public)
```

**Email Template:** `practice_invitation`
```
Subject: You're Invited to Join {platform_name}

Hi {owner_name},

You've been invited to set up your accounting practice on {platform_name}.

Practice Details:
- Practice Name: {practice_name}
- Plan: {plan_type}
- User Limit: {max_users}
- Client Limit: {max_clients}

Click below to accept the invitation and set up your account:
{acceptance_link}

This invitation expires on {expiry_date}.

If you have any questions, contact our support team.
```

**Frontend Components:**
- `InvitePracticeOwnerModal` - Form to create invitation
- `PracticeInvitationsList` - Table of all invitations with status
- `AcceptInvitationPage` - Public page for owners to accept

---

### 3.3 SuperAdmin Practice View & Support Access

**New Feature:** SuperAdmin can view and access any practice's data to provide support.

**Purpose:**
- Help practice owners troubleshoot issues
- View practice data without modifying
- Impersonate users for debugging (with audit trail)
- Provide hands-on support when needed

**Capabilities:**

| Feature | Description |
|---------|-------------|
| **View Practice Dashboard** | See practice metrics as owner sees them |
| **Browse Practice Data** | View clients, requests, documents, invoices |
| **View Settings** | See practice configuration and customizations |
| **View Activity Logs** | See all actions within the practice |
| **Impersonate User** | Act as any user in the practice (with logging) |
| **Read-Only Mode** | Browse without making changes |
| **Support Mode** | Make changes on behalf of practice (logged) |

**Database Models:**
```python
class SuperAdminAccess(db.Model):
    """Tracks when SuperAdmin accesses practice data"""
    id = db.Column(db.Integer, primary_key=True)

    super_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    access_type = db.Column(db.String(20))  # view, impersonate, support
    reason = db.Column(db.Text)  # Why accessing (for audit)

    # For impersonation
    impersonated_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

    # Track what was accessed
    pages_visited = db.Column(db.JSON)  # List of pages/endpoints accessed
    actions_taken = db.Column(db.JSON)  # Any modifications made

class ImpersonationSession(db.Model):
    """Active impersonation sessions"""
    id = db.Column(db.Integer, primary_key=True)

    super_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    session_token = db.Column(db.String(255), unique=True)
    reason = db.Column(db.Text, nullable=False)  # Required reason

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Auto-expire after 1 hour
    ended_at = db.Column(db.DateTime)
```

**API Endpoints:**
```
# Practice View Access
GET    /api/superadmin/practices/<id>/dashboard    # View practice dashboard
GET    /api/superadmin/practices/<id>/users        # View practice users
GET    /api/superadmin/practices/<id>/clients      # View practice clients
GET    /api/superadmin/practices/<id>/requests     # View service requests
GET    /api/superadmin/practices/<id>/documents    # View documents
GET    /api/superadmin/practices/<id>/invoices     # View invoices
GET    /api/superadmin/practices/<id>/settings     # View practice settings
GET    /api/superadmin/practices/<id>/activity     # View activity logs
GET    /api/superadmin/practices/<id>/email-templates # View email templates

# Impersonation
POST   /api/superadmin/impersonate                 # Start impersonation session
DELETE /api/superadmin/impersonate                 # End impersonation session
GET    /api/superadmin/impersonate/status          # Check current impersonation

# Support Actions (with audit)
POST   /api/superadmin/practices/<id>/support/reset-password  # Reset user password
POST   /api/superadmin/practices/<id>/support/unlock-user     # Unlock locked user
POST   /api/superadmin/practices/<id>/support/fix-data        # Data correction
```

**Frontend Components:**

```
SuperAdmin Practice View
├── PracticeSelector
│   └── Search/filter practices
├── PracticeOverview
│   ├── Practice Info Card
│   ├── Owner Details
│   ├── Plan & Usage Stats
│   └── Quick Actions
├── PracticeDataViewer
│   ├── Users Tab
│   ├── Clients Tab
│   ├── Requests Tab
│   ├── Documents Tab
│   ├── Invoices Tab
│   └── Settings Tab
├── ActivityLogViewer
│   └── Filter by date, user, action
├── ImpersonationControls
│   ├── Select User to Impersonate
│   ├── Enter Reason (required)
│   ├── Start Impersonation Button
│   └── Active Impersonation Banner
└── SupportActionsPanel
    ├── Reset Password
    ├── Unlock Account
    ├── Resend Invitation
    └── Data Fixes
```

**Impersonation UI Banner:**
When SuperAdmin is impersonating a user, show a persistent banner:
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚠️ IMPERSONATION MODE: Viewing as John Smith (Practice: ABC    │
│    Accounting) | Reason: Investigating login issue | [End]     │
└─────────────────────────────────────────────────────────────────┘
```

**Security & Audit Requirements:**

1. **Mandatory Reason:** SuperAdmin must provide reason before accessing practice data
2. **Full Audit Trail:** Every page view, action, and data access is logged
3. **Session Time Limit:** Impersonation sessions auto-expire after 1 hour
4. **Notification to Owner:** Optional - notify practice owner of support access
5. **Read-Only by Default:** View mode doesn't allow modifications
6. **Two-Factor for Impersonation:** Require 2FA before impersonating users
7. **Activity Report:** Generate report of all SuperAdmin access per practice

**Practice Owner Visibility:**
Practice owners can see when SuperAdmin accessed their data:
```python
# In Practice Settings > Security > Support Access Log
GET /api/companies/<id>/support-access-log
```

Shows:
- Date/time of access
- SuperAdmin name
- Reason provided
- Duration of access
- Actions taken (if any)

---

### 3.5 Feature Request Management

**New Feature:** Practice Owners can submit feature requests.

**Database Model:**
```python
class FeatureRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # ui, feature, integration, bug, etc.
    priority = db.Column(db.String(20))  # low, medium, high, critical

    status = db.Column(db.String(20))  # submitted, reviewing, planned, in_progress, completed, declined
    admin_response = db.Column(db.Text)

    votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**API Endpoints:**
```
POST   /api/feature-requests               # Submit request (Admin)
GET    /api/feature-requests               # List requests
GET    /api/feature-requests/<id>          # Get details
PATCH  /api/feature-requests/<id>          # Update status (SuperAdmin)
POST   /api/feature-requests/<id>/vote     # Vote for feature (Admin)
```

---

### 3.6 Support Ticket System

**New Feature:** Built-in support for Practice Owners.

**Database Model:**
```python
class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # technical, billing, feature, general
    priority = db.Column(db.String(20))  # low, medium, high, urgent

    status = db.Column(db.String(20))  # open, in_progress, waiting, resolved, closed
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class TicketMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    attachment_url = db.Column(db.String(500))
    is_internal = db.Column(db.Boolean, default=False)  # Internal notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 3.7 System Announcements

**New Feature:** SuperAdmin can broadcast announcements.

**Database Model:**
```python
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    type = db.Column(db.String(20))  # info, warning, maintenance, feature

    target_audience = db.Column(db.String(20))  # all, admins, accountants, clients
    target_companies = db.Column(db.JSON)  # Specific company IDs or null for all

    is_dismissible = db.Column(db.Boolean, default=True)
    show_from = db.Column(db.DateTime)
    show_until = db.Column(db.DateTime)

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 3.5 Plan & Subscription Management

**New Feature:** Manage practice subscriptions.

**Database Model:**
```python
class SubscriptionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # starter, standard, premium, enterprise

    # Limits
    max_users = db.Column(db.Integer)
    max_clients = db.Column(db.Integer)
    max_storage_gb = db.Column(db.Integer)

    # Features
    features = db.Column(db.JSON)  # List of enabled features

    # Pricing
    monthly_price = db.Column(db.Numeric(10, 2))
    annual_price = db.Column(db.Numeric(10, 2))

    is_active = db.Column(db.Boolean, default=True)

class CompanySubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'))

    billing_cycle = db.Column(db.String(20))  # monthly, annual
    started_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

    status = db.Column(db.String(20))  # active, past_due, cancelled, trial
    trial_ends_at = db.Column(db.DateTime)
```

---

## 4. Client Management Enhancements

### 4.1 Client Portal Customization

**Features for Practice Owners:**

| Feature | Description |
|---------|-------------|
| **Welcome Message** | Custom message on client dashboard |
| **Portal Theme** | Match practice branding |
| **Available Services** | Control which services clients see |
| **Document Categories** | Custom document folder structure |
| **Self-Service Options** | Enable/disable client capabilities |

---

### 4.2 Client Onboarding Workflow

**New Feature:** Structured client onboarding.

**Workflow:**
```
Client Invited
    ↓
Welcome Email Sent
    ↓
Client Creates Account
    ↓
Onboarding Form Displayed
    ↓
Documents Requested
    ↓
Documents Uploaded
    ↓
Admin Reviews & Approves
    ↓
Client Activated
```

**Database Model:**
```python
class ClientOnboarding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    status = db.Column(db.String(20))  # invited, registered, form_pending, docs_pending, review, completed

    form_completed_at = db.Column(db.DateTime)
    documents_submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    required_documents = db.Column(db.JSON)  # List of required doc types
    submitted_documents = db.Column(db.JSON)  # List of submitted doc IDs
```

---

### 4.3 Client Tags Management

**New Feature:** Practice Owners can create and assign custom tags to clients for organization and filtering.

**Current State:** Basic tag functionality exists but needs enhancement.

**Enhanced Capabilities:**

| Feature | Description |
|---------|-------------|
| **Create Custom Tags** | Define tags specific to the practice |
| **Color Coding** | Assign colors for visual identification |
| **Tag Categories** | Organize tags into categories |
| **Bulk Tagging** | Apply tags to multiple clients at once |
| **Tag-Based Filtering** | Filter client list by tags |
| **Tag-Based Actions** | Send bulk emails, generate reports by tag |
| **Auto-Tagging Rules** | Automatically apply tags based on conditions |

**Database Models:**
```python
class ClientTag(db.Model):
    """Custom tags created by practice owners"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6B7280')  # Hex color
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))  # Optional icon name

    # Organization
    category_id = db.Column(db.Integer, db.ForeignKey('tag_categories.id'), nullable=True)

    # Usage tracking
    client_count = db.Column(db.Integer, default=0)  # Cached count

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='unique_company_tag'),
    )

class TagCategory(db.Model):
    """Categories to organize tags"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    name = db.Column(db.String(50), nullable=False)  # e.g., "Client Type", "Service", "Priority"
    description = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)

class ClientTagAssignment(db.Model):
    """Many-to-many relationship between clients and tags"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('client_tags.id'), nullable=False)

    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('client_id', 'tag_id', name='unique_client_tag'),
    )

class AutoTagRule(db.Model):
    """Rules for automatic tag assignment"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('client_tags.id'), nullable=False)

    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

    # Rule conditions (JSON)
    conditions = db.Column(db.JSON)
    # Examples:
    # {"field": "total_revenue", "operator": ">", "value": 10000}
    # {"field": "services_used", "operator": "contains", "value": "tax-return"}
    # {"field": "days_since_last_request", "operator": ">", "value": 180}

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Suggested Default Tags:**

| Tag Name | Color | Category | Description |
|----------|-------|----------|-------------|
| **Premium** | Gold (#F59E0B) | Client Type | High-value clients |
| **VIP** | Purple (#8B5CF6) | Client Type | Top priority clients |
| **New Client** | Green (#10B981) | Status | Recently onboarded |
| **At Risk** | Red (#EF4444) | Status | May need attention |
| **Tax Return** | Blue (#3B82F6) | Service | Uses tax return service |
| **BAS** | Blue (#3B82F6) | Service | Uses BAS service |
| **Bookkeeping** | Blue (#3B82F6) | Service | Uses bookkeeping service |
| **SMSF** | Blue (#3B82F6) | Service | Uses SMSF service |
| **Individual** | Gray (#6B7280) | Entity Type | Individual client |
| **Company** | Gray (#6B7280) | Entity Type | Business client |
| **Trust** | Gray (#6B7280) | Entity Type | Trust client |
| **Overdue** | Orange (#F97316) | Billing | Has overdue payments |
| **Referred** | Pink (#EC4899) | Source | Came via referral |

**API Endpoints:**
```
# Tag Management (Practice Owner/Admin)
POST   /api/tags                              # Create new tag
GET    /api/tags                              # List all tags for practice
GET    /api/tags/<id>                         # Get tag details
PATCH  /api/tags/<id>                         # Update tag
DELETE /api/tags/<id>                         # Delete tag (removes from all clients)

# Tag Categories
POST   /api/tags/categories                   # Create category
GET    /api/tags/categories                   # List categories
PATCH  /api/tags/categories/<id>              # Update category
DELETE /api/tags/categories/<id>              # Delete category

# Assign/Remove Tags from Clients
POST   /api/clients/<id>/tags                 # Assign tags to client
DELETE /api/clients/<id>/tags/<tag_id>        # Remove tag from client
GET    /api/clients/<id>/tags                 # Get client's tags

# Bulk Tagging
POST   /api/tags/<id>/bulk-assign             # Assign tag to multiple clients
POST   /api/tags/<id>/bulk-remove             # Remove tag from multiple clients

# Tag-Based Queries
GET    /api/clients?tags=premium,vip          # Filter clients by tags
GET    /api/tags/<id>/clients                 # Get all clients with tag

# Auto-Tag Rules
POST   /api/tags/auto-rules                   # Create auto-tag rule
GET    /api/tags/auto-rules                   # List rules
PATCH  /api/tags/auto-rules/<id>              # Update rule
DELETE /api/tags/auto-rules/<id>              # Delete rule
POST   /api/tags/auto-rules/<id>/run          # Manually run rule
```

**Frontend: Tag Management UI**

```
┌─────────────────────────────────────────────────────────────────┐
│ Client Tags                                    [+ Create Tag]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ FILTER: [All Categories ▼]  [Search tags...]                    │
│                                                                  │
│ CLIENT TYPE                                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🏷️ Premium          ████ Gold      12 clients    [Edit] [×] │ │
│ │ 🏷️ VIP              ████ Purple     5 clients    [Edit] [×] │ │
│ │ 🏷️ New Client       ████ Green      8 clients    [Edit] [×] │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ SERVICE                                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🏷️ Tax Return       ████ Blue      34 clients    [Edit] [×] │ │
│ │ 🏷️ BAS              ████ Blue      28 clients    [Edit] [×] │ │
│ │ 🏷️ Bookkeeping      ████ Blue      15 clients    [Edit] [×] │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ STATUS                                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🏷️ At Risk          ████ Red        3 clients    [Edit] [×] │ │
│ │ 🏷️ Overdue          ████ Orange     7 clients    [Edit] [×] │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Client Profile - Tag Assignment:**

```
┌─────────────────────────────────────────────────────────────────┐
│ John Smith                                                       │
│ john.smith@email.com                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ TAGS                                                    [+ Add]  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🏷️ Premium  🏷️ Tax Return  🏷️ Individual        [Manage]   │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ Add Tags:                                                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Search or select tags...]                                   │ │
│ │ ☐ VIP           ☐ BAS          ☐ Bookkeeping                │ │
│ │ ☐ At Risk       ☐ SMSF         ☐ Company                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Client List with Tag Filters:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Clients                                         [+ Add Client]   │
├─────────────────────────────────────────────────────────────────┤
│ FILTERS:                                                         │
│ Tags: [Premium ×] [Tax Return ×]  [+ Add Filter]  [Clear All]   │
│                                                                  │
│ Showing 12 clients matching filters                              │
├─────────────────────────────────────────────────────────────────┤
│ ☐ │ Name           │ Email              │ Tags           │ ... │
│───┼────────────────┼────────────────────┼────────────────┼─────│
│ ☐ │ John Smith     │ john@email.com     │ 🏷️Premium 🏷️Tax│     │
│ ☐ │ Jane Doe       │ jane@email.com     │ 🏷️Premium 🏷️Tax│     │
│ ☐ │ Bob Wilson     │ bob@email.com      │ 🏷️Premium 🏷️Tax│     │
├─────────────────────────────────────────────────────────────────┤
│ Selected: 0  │ [Bulk Actions ▼]                                  │
│              │  • Add Tags                                       │
│              │  • Remove Tags                                    │
│              │  • Send Email                                     │
│              │  • Export                                         │
└─────────────────────────────────────────────────────────────────┘
```

**Auto-Tagging Rules Example:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Auto-Tag Rules                                  [+ Create Rule]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Rule: Mark Premium Clients                        ● Active   │ │
│ │ Tag: Premium                                                 │ │
│ │ Condition: Total Revenue > $5,000                           │ │
│ │ Last Run: Jan 15, 2024 | Affected: 12 clients               │ │
│ │                                         [Edit] [Run] [Delete]│ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Rule: Flag At-Risk Clients                        ● Active   │ │
│ │ Tag: At Risk                                                 │ │
│ │ Condition: Days Since Last Request > 180                    │ │
│ │ Last Run: Jan 15, 2024 | Affected: 3 clients                │ │
│ │                                         [Edit] [Run] [Delete]│ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4.4 Client Groups & Segments

**New Feature:** Group clients for bulk operations.

**Database Model:**
```python
class ClientGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    color = db.Column(db.String(7))

    # Smart group rules (auto-membership)
    is_smart = db.Column(db.Boolean, default=False)
    rules = db.Column(db.JSON)  # e.g., {"tag": "premium", "service": "tax-return"}

class ClientGroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('client_groups.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
```

**Use Cases:**
- Bulk email to group
- Group-specific pricing
- Service availability per group
- Reporting by segment

---

### 4.5 Client Communication History

**New Feature:** Unified communication timeline.

**Database Model:**
```python
class CommunicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    type = db.Column(db.String(20))  # email, sms, call, meeting, note
    direction = db.Column(db.String(10))  # inbound, outbound

    subject = db.Column(db.String(255))
    content = db.Column(db.Text)

    related_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'))

    logged_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 5. Billing & Invoice Features

### 5.1 Invoice Management System

**Current State:** Basic invoice tracking (raised/paid flags).

**Enhancement:**

**Database Model:**
```python
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'))

    invoice_number = db.Column(db.String(50), unique=True)

    # Amounts
    subtotal = db.Column(db.Numeric(10, 2))
    tax_amount = db.Column(db.Numeric(10, 2))
    discount_amount = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))

    # Dates
    issue_date = db.Column(db.Date)
    due_date = db.Column(db.Date)

    # Status
    status = db.Column(db.String(20))  # draft, sent, viewed, paid, overdue, cancelled

    # Payment
    paid_amount = db.Column(db.Numeric(10, 2), default=0)
    paid_at = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))

    notes = db.Column(db.Text)
    terms = db.Column(db.Text)

class InvoiceLineItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))

    description = db.Column(db.String(255))
    quantity = db.Column(db.Numeric(10, 2))
    unit_price = db.Column(db.Numeric(10, 2))
    tax_rate = db.Column(db.Numeric(5, 2))
    amount = db.Column(db.Numeric(10, 2))
```

---

### 5.2 Payment Gateway Integration

**Recommended Integrations:**
- Stripe (International)
- PayPal (International)
- Square (AU/NZ)
- eWay (Australia)

**Features:**
- Online payment links in invoices
- Automatic payment reconciliation
- Recurring payments for retainer clients
- Payment reminders automation

---

### 5.3 Quote/Estimate System

**New Feature:** Create and send quotes before invoicing.

**Database Model:**
```python
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    quote_number = db.Column(db.String(50), unique=True)

    # Items (similar to invoice)
    subtotal = db.Column(db.Numeric(10, 2))
    tax_amount = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))

    # Validity
    issue_date = db.Column(db.Date)
    valid_until = db.Column(db.Date)

    # Status
    status = db.Column(db.String(20))  # draft, sent, accepted, declined, expired, converted

    # Conversion
    converted_to_invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    accepted_at = db.Column(db.DateTime)
```

---

### 5.4 Recurring Invoices

**New Feature:** Automatic invoice generation for retainer clients.

**Database Model:**
```python
class RecurringInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Template
    line_items = db.Column(db.JSON)
    total_amount = db.Column(db.Numeric(10, 2))

    # Schedule
    frequency = db.Column(db.String(20))  # weekly, monthly, quarterly, annually
    day_of_month = db.Column(db.Integer)  # For monthly
    next_invoice_date = db.Column(db.Date)

    # Options
    auto_send = db.Column(db.Boolean, default=True)
    auto_charge = db.Column(db.Boolean, default=False)

    is_active = db.Column(db.Boolean, default=True)
```

---

## 6. Communication & Notification Features

### 6.1 SMS Notifications

**New Feature:** SMS support alongside email.

**Recommended Providers:**
- Twilio (International)
- MessageMedia (Australia)
- Sinch (International)

**Use Cases:**
- Appointment reminders
- Document request alerts
- Payment reminders
- 2FA codes

**Database Model:**
```python
class SMSTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    name = db.Column(db.String(100))
    slug = db.Column(db.String(50))
    content = db.Column(db.String(160))  # SMS character limit
    variables = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
```

---

### 6.2 In-App Notification Center

**Enhancement:** Rich notification system.

**Features:**
- Bell icon with unread count
- Notification categories (requests, documents, payments, system)
- Mark as read/unread
- Notification preferences
- Push notifications (PWA)

**Database Model:**
```python
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    type = db.Column(db.String(50))  # request_update, document_received, payment, etc.
    title = db.Column(db.String(200))
    message = db.Column(db.Text)

    # Link to related entity
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)

    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 6.3 Notification Preferences

**New Feature:** User-controlled notification settings.

**Database Model:**
```python
class NotificationPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    notification_type = db.Column(db.String(50))

    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    push_enabled = db.Column(db.Boolean, default=True)
    in_app_enabled = db.Column(db.Boolean, default=True)
```

---

### 6.4 Secure Messaging Portal

**Enhancement:** Enhanced query/messaging system.

**Features:**
- Thread-based conversations
- File attachments
- Read receipts
- Message templates for common responses
- Canned responses library

---

## 7. Reporting & Analytics

### 7.1 Practice Dashboard

**Enhanced Metrics for Practice Owners:**

| Metric | Description |
|--------|-------------|
| **Revenue Overview** | Total invoiced, paid, outstanding |
| **Client Growth** | New clients this month/year |
| **Request Volume** | Requests by status, service type |
| **Team Performance** | Requests completed per accountant |
| **Average Turnaround** | Time from submission to completion |
| **Client Satisfaction** | Review scores (if implemented) |
| **Document Status** | Pending documents by client |
| **Upcoming Deadlines** | Tax dates, BAS dates |

---

### 7.2 Custom Report Builder

**New Feature:** Practice Owners create custom reports.

**Report Types:**
- Client list with custom fields
- Revenue by service/client/period
- Request aging report
- Team utilization report
- Document compliance report

**Export Formats:**
- PDF
- Excel
- CSV

---

### 7.3 Scheduled Reports

**New Feature:** Automatic report delivery.

**Database Model:**
```python
class ScheduledReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    name = db.Column(db.String(100))
    report_type = db.Column(db.String(50))
    filters = db.Column(db.JSON)

    frequency = db.Column(db.String(20))  # daily, weekly, monthly
    day_of_week = db.Column(db.Integer)  # For weekly
    day_of_month = db.Column(db.Integer)  # For monthly

    recipients = db.Column(db.JSON)  # List of email addresses
    format = db.Column(db.String(10))  # pdf, excel, csv

    is_active = db.Column(db.Boolean, default=True)
    last_sent_at = db.Column(db.DateTime)
```

---

### 7.4 Client Activity Reports

**New Feature:** Per-client activity summary.

**Includes:**
- Service history
- Document submissions
- Payment history
- Communication log
- Outstanding items

---

## 8. Document Management

### 8.1 Document Categories & Folders

**Enhancement:** Organized document structure.

**Database Model:**
```python
class DocumentCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('document_categories.id'))
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))

    is_system = db.Column(db.Boolean, default=False)
```

**Default Categories:**
- Identity Documents
- Tax Returns
- Financial Statements
- Bank Statements
- Receipts & Expenses
- Contracts & Agreements
- Correspondence

---

### 8.2 Document Templates

**New Feature:** Pre-formatted document templates.

**Features:**
- Engagement letters
- Client agreements
- Information request checklists
- Tax organizers

---

### 8.3 Document Requests

**Enhancement:** Structured document collection.

**Database Model:**
```python
class DocumentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'))

    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    documents_requested = db.Column(db.JSON)  # List of document types
    due_date = db.Column(db.Date)

    status = db.Column(db.String(20))  # pending, partial, complete

    reminder_sent = db.Column(db.Boolean, default=False)
    reminder_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
```

---

### 8.4 Document Versioning

**New Feature:** Track document versions.

**Database Model:**
```python
class DocumentVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))

    version_number = db.Column(db.Integer)
    file_url = db.Column(db.String(500))
    file_size = db.Column(db.Integer)

    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    change_notes = db.Column(db.Text)
```

---

### 8.5 E-Signature Integration

**Recommended Integrations:**
- DocuSign
- Adobe Sign
- HelloSign

**Use Cases:**
- Engagement letters
- Tax return authorizations
- Client agreements

---

## 9. Calendar & Scheduling

### 9.1 Practice Calendar

**New Feature:** Integrated calendar view.

**Features:**
- Tax deadlines
- BAS due dates
- Client appointments
- Team availability
- Task due dates

---

### 9.2 Appointment Booking

**New Feature:** Client self-scheduling.

**Database Model:**
```python
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    type = db.Column(db.String(20))  # in_person, video, phone
    location = db.Column(db.String(255))
    meeting_link = db.Column(db.String(500))

    status = db.Column(db.String(20))  # scheduled, confirmed, completed, cancelled, no_show

    notes = db.Column(db.Text)

    reminder_sent = db.Column(db.Boolean, default=False)

class StaffAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    day_of_week = db.Column(db.Integer)  # 0-6
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    is_available = db.Column(db.Boolean, default=True)
```

---

### 9.3 Deadline Tracking

**New Feature:** Automated deadline management.

**Database Model:**
```python
class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    type = db.Column(db.String(50))  # tax_return, bas, super, payroll_tax
    description = db.Column(db.String(255))

    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    # Reminders
    reminder_30_days = db.Column(db.Boolean, default=False)
    reminder_14_days = db.Column(db.Boolean, default=False)
    reminder_7_days = db.Column(db.Boolean, default=False)
```

---

## 10. Compliance & Audit

### 10.1 Audit Trail Enhancement

**Current State:** Basic activity logging.

**Enhancement:**
- Before/after values for all changes
- IP address logging
- Device information
- Session tracking
- Export audit logs

---

### 10.2 Data Retention Policies

**New Feature:** Configurable data retention.

**Database Model:**
```python
class RetentionPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    entity_type = db.Column(db.String(50))  # documents, requests, messages
    retention_years = db.Column(db.Integer)

    auto_archive = db.Column(db.Boolean, default=True)
    auto_delete = db.Column(db.Boolean, default=False)
```

---

### 10.3 GDPR/Privacy Compliance

**New Features:**
- Data export (client request)
- Data deletion (right to be forgotten)
- Consent tracking
- Privacy policy acceptance

---

### 10.4 ATO Integration Readiness

**Future Feature:** Direct ATO lodgement.

**Considerations:**
- SBR (Standard Business Reporting) compliance
- Digital signing
- Secure transmission
- Lodgement receipts

---

## 11. Integration Features

### 11.1 Accounting Software Integration

**Recommended Integrations:**

| Software | Use Case |
|----------|----------|
| **Xero** | Bank feeds, invoicing, reconciliation |
| **MYOB** | Australian accounting standard |
| **QuickBooks** | International compatibility |

---

### 11.2 Cloud Storage Integration

**Options:**
- Google Drive
- OneDrive/SharePoint
- Dropbox Business

---

### 11.3 Calendar Integration

**Options:**
- Google Calendar
- Microsoft Outlook
- Apple Calendar (via CalDAV)

---

### 11.4 Communication Integration

**Options:**
- Microsoft Teams
- Slack
- Zoom (for video meetings)

---

### 11.5 Webhook Support

**New Feature:** Real-time event notifications.

**Database Model:**
```python
class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    name = db.Column(db.String(100))
    url = db.Column(db.String(500))
    secret = db.Column(db.String(255))

    events = db.Column(db.JSON)  # ['request.created', 'invoice.paid', etc.]

    is_active = db.Column(db.Boolean, default=True)

    last_triggered_at = db.Column(db.DateTime)
    failure_count = db.Column(db.Integer, default=0)
```

---

### 11.6 API Access for Practice Owners

**New Feature:** Practice-level API keys.

**Database Model:**
```python
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    name = db.Column(db.String(100))
    key_hash = db.Column(db.String(255))  # Hashed API key

    permissions = db.Column(db.JSON)  # Scoped permissions

    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
```

---

## 12. Implementation Priority Matrix

### Priority 1: High Impact, Low Effort

| Feature | Effort | Impact |
|---------|--------|--------|
| Extended email templates | Low | High |
| Email automation triggers | Medium | High |
| Client communication history | Low | High |
| Practice settings dashboard | Medium | High |
| Notification preferences | Low | Medium |

### Priority 2: High Impact, Medium Effort

| Feature | Effort | Impact |
|---------|--------|--------|
| Tenant-specific services | Medium | High |
| Custom form builder for admins | Medium | High |
| Invoice management system | Medium | High |
| Document categories | Medium | Medium |
| Practice calendar | Medium | High |

### Priority 3: High Impact, High Effort

| Feature | Effort | Impact |
|---------|--------|--------|
| Payment gateway integration | High | High |
| Appointment booking system | High | High |
| Custom report builder | High | Medium |
| Xero/MYOB integration | High | High |
| E-signature integration | High | Medium |

### Priority 4: Future Roadmap

| Feature | Effort | Impact |
|---------|--------|--------|
| SMS notifications | Medium | Medium |
| ATO integration | Very High | High |
| Mobile app | Very High | Medium |
| AI document categorization | High | Medium |
| Client portal mobile app | High | Medium |

---

## Summary

This enhancement document outlines **50+ feature improvements** across 11 categories, focusing on:

1. **Empowering Practice Owners** with customization options
2. **Comprehensive email template system** for client communication
3. **Structured SuperAdmin management** for practice requests
4. **Enhanced billing and invoicing** capabilities
5. **Better client management** and communication tools
6. **Robust reporting and analytics**
7. **Integration readiness** for popular tools

Implementation should follow the priority matrix, starting with high-impact, low-effort features to deliver quick wins while planning for larger integrations.

---

*Document Version: 1.0*
*Last Updated: January 2026*
