# Accountant CRM - Business Documentation

> **Version:** 1.0
> **Last Updated:** January 2026
> **Audience:** Business Development, Sales, Marketing Teams

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Product Overview](#product-overview)
3. [Target Market](#target-market)
4. [User Roles & Personas](#user-roles--personas)
5. [Feature Catalog](#feature-catalog)
6. [Pricing & Plans](#pricing--plans)
7. [Key Workflows](#key-workflows)
8. [Competitive Advantages](#competitive-advantages)
9. [Integration Capabilities](#integration-capabilities)
10. [Security & Compliance](#security--compliance)
11. [Technical Specifications](#technical-specifications)
12. [Frequently Asked Questions](#frequently-asked-questions)
13. [Glossary](#glossary)

---

## Executive Summary

**Accountant CRM** is a multi-tenant Software-as-a-Service (SaaS) platform designed specifically for accounting practices in Australia. It streamlines client management, service delivery, document handling, and billing workflows for accounting firms of all sizes.

### Key Value Propositions

| For Accounting Practices | For Their Clients |
|--------------------------|-------------------|
| Centralized client management | Self-service portal |
| Automated workflows | Real-time status tracking |
| Professional invoicing with online payments | Easy document uploads |
| Custom forms for data collection | Secure communication |
| Team workload management | Mobile-friendly interface |
| White-label branding options | Transparent pricing |

### Quick Stats

- **Multi-tenant architecture** - Each practice gets isolated data
- **4 subscription tiers** - Starter to Enterprise
- **Stripe integration** - Accept online payments instantly
- **Australian-focused** - GST, TFN, ABN, SMSF support built-in
- **Email automation** - 12 trigger types for automated communications

---

## Product Overview

### What is Accountant CRM?

Accountant CRM is a purpose-built practice management solution that helps accounting firms:

1. **Manage Clients** - Store client information, documents, and communication history
2. **Deliver Services** - Track service requests from submission to completion
3. **Collect Information** - Custom forms for tax returns, BAS, company setup, etc.
4. **Bill Clients** - Professional invoicing with Stripe payment integration
5. **Communicate** - Email templates, automation, and in-app messaging
6. **Collaborate** - Assign work to team members and track progress

### Platform Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SUPER ADMIN                               │
│              (Platform Owner / Your Company)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   Practice A  │       │   Practice B  │       │   Practice C  │
│   (Tenant 1)  │       │   (Tenant 2)  │       │   (Tenant 3)  │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ Practice Owner│       │ Practice Owner│       │ Practice Owner│
│ Accountants   │       │ Accountants   │       │ Accountants   │
│ Clients       │       │ Clients       │       │ Clients       │
└───────────────┘       └───────────────┘       └───────────────┘
```

---

## Target Market

### Primary Market

**Australian Accounting Practices** including:

- Sole practitioners
- Small accounting firms (2-10 staff)
- Medium practices (10-50 staff)
- Large multi-office firms (50+ staff)

### Ideal Customer Profile

| Attribute | Description |
|-----------|-------------|
| **Industry** | Accounting, Tax, Bookkeeping, Financial Services |
| **Location** | Australia (designed for AU compliance) |
| **Size** | 1-100+ employees |
| **Current Pain Points** | Manual processes, spreadsheets, disconnected tools |
| **Tech Readiness** | Moderate - looking for easy-to-use solutions |
| **Decision Maker** | Practice Owner, Managing Partner, Operations Manager |

### Market Segments

| Segment | Characteristics | Recommended Plan |
|---------|-----------------|------------------|
| **Sole Practitioners** | 1 accountant, <50 clients | Starter |
| **Small Firms** | 2-5 accountants, 50-100 clients | Standard |
| **Growing Practices** | 5-20 accountants, 100-500 clients | Premium |
| **Large Firms** | 20+ accountants, 500+ clients | Enterprise |

---

## User Roles & Personas

### Role Hierarchy

```
Super Admin (Platform Level)
    │
    └── Practice Owner (Company Level)
            │
            ├── Accountant (Staff)
            │
            └── Client (End User)
```

### Detailed Role Descriptions

#### 1. Super Admin (Platform Owner)

**Who:** Your internal team managing the SaaS platform

**Capabilities:**
- Create and manage accounting practices (tenants)
- Set subscription plans and limits
- Access all practices for support purposes
- Impersonate users for troubleshooting
- View platform-wide analytics
- Manage system-wide email templates
- Configure default services and forms

**Use Cases:**
- Onboarding new accounting practices
- Providing technical support
- Monitoring platform health
- Managing billing and subscriptions

---

#### 2. Practice Owner

**Who:** The accounting firm owner or managing partner

**Capabilities:**
- Full control over their practice
- Invite and manage accountants
- Invite and manage clients
- Customize services offered
- Create and clone forms
- Access all client data and requests
- View practice analytics and reports
- Configure practice branding
- Manage email templates
- Handle invoicing and payments

**Pain Points Addressed:**
- "I can't see what my team is working on"
- "Client onboarding takes too long"
- "I'm using 5 different tools that don't talk to each other"
- "Chasing payments is time-consuming"

---

#### 3. Accountant (Staff)

**Who:** Employed accountants, bookkeepers, tax agents

**Capabilities:**
- View assigned client requests
- Process service requests
- Communicate with clients via queries
- Upload and manage documents
- Add internal notes
- View client history
- Tag and categorize clients

**Pain Points Addressed:**
- "I don't know which clients need attention"
- "Client documents are scattered everywhere"
- "I waste time chasing clients for information"

---

#### 4. Client (End User)

**Who:** Individuals or businesses using the accounting services

**Capabilities:**
- Request services
- Fill out required forms
- Upload documents
- Track request status
- Respond to accountant queries
- View and pay invoices
- Access their document history
- Update their profile information

**Pain Points Addressed:**
- "I never know what's happening with my tax return"
- "I keep forgetting what documents to provide"
- "Paying invoices is inconvenient"

---

## Feature Catalog

### Core Features (All Plans)

#### Client Management
| Feature | Description | Benefit |
|---------|-------------|---------|
| Client Profiles | Comprehensive client information storage | Single source of truth |
| Contact Details | Phone, email, address management | Easy communication |
| Document Storage | Secure Azure cloud storage | No more lost documents |
| Client Tags | Categorize clients with custom labels | Easy filtering and organization |
| Activity History | Complete audit trail | Full transparency |

#### Service Request Management
| Feature | Description | Benefit |
|---------|-------------|---------|
| Service Catalog | Define services with pricing | Professional service menu |
| Request Workflow | Pending → Assigned → Processing → Completed | Clear progress tracking |
| Assignment System | Assign requests to accountants | Balanced workload |
| Status Tracking | Real-time status updates | Client transparency |
| Query System | Two-way messaging on requests | Efficient communication |
| Internal Notes | Private notes for staff | Team collaboration |

#### Form Builder
| Feature | Description | Benefit |
|---------|-------------|---------|
| 11 Question Types | Text, select, date, file, checkbox, etc. | Flexible data collection |
| Conditional Logic | Show/hide questions based on answers | Smart, dynamic forms |
| Repeatable Sections | Handle multiple directors, properties, etc. | Complex data structures |
| Form Templates | Pre-built forms for common services | Quick setup |
| Response Snapshots | Immutable form submission records | Data integrity |

#### Document Management
| Feature | Description | Benefit |
|---------|-------------|---------|
| Secure Upload | Encrypted file storage | Data security |
| Category Organization | Tax returns, ID docs, supporting docs | Easy retrieval |
| SAS Token Access | Time-limited secure download links | Controlled access |
| Multiple File Types | PDF, images, Office documents | Flexibility |

### Advanced Features

#### Invoicing & Payments
| Feature | Description | Plans |
|---------|-------------|-------|
| Professional Invoices | Branded, itemized invoices | All |
| Automatic Numbering | INV-YYYY-XXXXX format | All |
| GST Calculations | Australian tax compliance | All |
| Line Items | Multiple services per invoice | All |
| Payment Tracking | Partial and full payments | All |
| **Stripe Integration** | Online card payments | Standard+ |
| **Checkout Sessions** | Hosted payment pages | Standard+ |
| **Webhook Reconciliation** | Automatic payment updates | Standard+ |
| **Payment Links** | Shareable payment URLs | Standard+ |

#### Email & Communication
| Feature | Description | Plans |
|---------|-------------|-------|
| Email Templates | Customizable templates | All |
| Template Variables | Dynamic content insertion | All |
| Bulk Email | Send to multiple clients | Standard+ |
| **Recipient Filtering** | Filter by role, tags, status | Standard+ |
| **Scheduled Emails** | Send at future date/time | Premium+ |
| **Email Automation** | Trigger-based emails | Premium+ |
| **12 Trigger Types** | Registration, invoice, birthday, etc. | Premium+ |

#### Analytics & Reporting
| Feature | Description | Plans |
|---------|-------------|-------|
| Dashboard Metrics | Key performance indicators | All |
| Request Statistics | Volume, status, completion rates | All |
| Revenue Tracking | Income analysis | Standard+ |
| Workload Analysis | Staff utilization | Standard+ |
| Bottleneck Detection | Identify process issues | Premium+ |
| CSV Export | Data export capabilities | All |

#### Administration
| Feature | Description | Plans |
|---------|-------------|-------|
| User Management | Add/remove team members | All |
| Role-Based Access | Granular permissions | All |
| Activity Logging | Complete audit trail | All |
| **Plan Limits** | Usage enforcement | All |
| **User Impersonation** | Support access (Super Admin) | Enterprise |
| **Custom Branding** | Logo, colors | Premium+ |

---

## Pricing & Plans

### Plan Comparison

| Feature | Starter | Standard | Premium | Enterprise |
|---------|:-------:|:--------:|:-------:|:----------:|
| **Monthly Price** | $49 | $99 | $199 | Custom |
| **Users (Staff)** | 5 | 10 | 50 | Unlimited |
| **Clients** | 50 | 100 | 500 | Unlimited |
| **Services** | 10 | 25 | Unlimited | Unlimited |
| **Forms** | 5 | 15 | Unlimited | Unlimited |
| **Storage** | 5 GB | 20 GB | 100 GB | Unlimited |
| | | | | |
| **Core Features** | ✅ | ✅ | ✅ | ✅ |
| **Document Storage** | ✅ | ✅ | ✅ | ✅ |
| **Basic Analytics** | ✅ | ✅ | ✅ | ✅ |
| **Email Templates** | ✅ | ✅ | ✅ | ✅ |
| | | | | |
| **Stripe Payments** | ❌ | ✅ | ✅ | ✅ |
| **Bulk Email** | ❌ | ✅ | ✅ | ✅ |
| **Advanced Analytics** | ❌ | ✅ | ✅ | ✅ |
| | | | | |
| **Email Automation** | ❌ | ❌ | ✅ | ✅ |
| **Scheduled Emails** | ❌ | ❌ | ✅ | ✅ |
| **Custom Branding** | ❌ | ❌ | ✅ | ✅ |
| **API Access** | ❌ | ❌ | ✅ | ✅ |
| | | | | |
| **Dedicated Support** | ❌ | ❌ | ❌ | ✅ |
| **Custom Integrations** | ❌ | ❌ | ❌ | ✅ |
| **SLA Guarantee** | ❌ | ❌ | ❌ | ✅ |
| **On-premise Option** | ❌ | ❌ | ❌ | ✅ |

### Plan Details

#### Starter Plan - $49/month
*Perfect for sole practitioners just starting out*

- Up to 5 staff members
- Up to 50 clients
- 10 services, 5 forms
- 5 GB document storage
- Email support

#### Standard Plan - $99/month
*For small firms ready to grow*

- Up to 10 staff members
- Up to 100 clients
- 25 services, 15 forms
- 20 GB document storage
- Stripe payment integration
- Bulk email with recipient filtering
- Priority email support

#### Premium Plan - $199/month
*For established practices wanting automation*

- Up to 50 staff members
- Up to 500 clients
- Unlimited services and forms
- 100 GB document storage
- Email automation (12 triggers)
- Scheduled email campaigns
- Custom branding (logo, colors)
- API access
- Phone support

#### Enterprise Plan - Custom Pricing
*For large firms with specific needs*

- Unlimited users and clients
- Unlimited storage
- All Premium features
- Dedicated account manager
- Custom integrations
- 99.9% SLA guarantee
- On-premise deployment option
- Custom feature development

---

## Key Workflows

### 1. Client Onboarding Workflow

```
┌─────────────────┐
│ Practice Owner  │
│ invites client  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ System sends    │
│ welcome email   │
│ with credentials│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Client logs in  │
│ & completes     │
│ profile         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Client requests │
│ first service   │
└─────────────────┘
```

**Email Automation Opportunity:**
- Welcome email on registration
- Profile completion reminder after 3 days
- Service recommendation after 7 days

---

### 2. Service Request Workflow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   PENDING    │────▶│   ASSIGNED   │────▶│  PROCESSING  │
│              │     │              │     │              │
│ Client       │     │ Owner assigns│     │ Accountant   │
│ submits      │     │ to accountant│     │ works on it  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌──────────────┐              │
                     │   QUERY      │◀─────────────┤
                     │   RAISED     │              │
                     │              │              │
                     │ Need more    │──────────────┘
                     │ info from    │   Client responds
                     │ client       │
                     └──────────────┘
                                                  │
                                                  ▼
                     ┌──────────────┐     ┌──────────────┐
                     │   INVOICED   │◀────│  COMPLETED   │
                     │              │     │              │
                     │ Invoice sent │     │ Work done    │
                     │ to client    │     │              │
                     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    PAID      │
                     │              │
                     │ Payment      │
                     │ received     │
                     └──────────────┘
```

---

### 3. Invoice & Payment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    INVOICE LIFECYCLE                         │
└─────────────────────────────────────────────────────────────┘

  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  DRAFT  │───▶│  SENT   │───▶│ VIEWED  │───▶│  PAID   │
  └─────────┘    └─────────┘    └─────────┘    └─────────┘
       │              │              │              │
       │              │              │              │
   Create         Email to      Client         Stripe
   invoice        client        opens it       webhook
   with items                                  confirms
                                               payment

                      │
                      ▼ (if not paid by due date)
                 ┌─────────┐
                 │ OVERDUE │
                 └─────────┘
                      │
                      │ Email automation:
                      │ Payment reminder
                      ▼
```

**Stripe Payment Flow:**
1. Accountant creates invoice with line items
2. System calculates GST automatically
3. Invoice sent to client via email
4. Client clicks "Pay Now" → Stripe Checkout
5. Client enters card details on secure Stripe page
6. Payment processed → Webhook notifies system
7. Invoice automatically marked as paid
8. Receipt email sent to client

---

### 4. Email Automation Triggers

| Trigger | When It Fires | Example Use |
|---------|---------------|-------------|
| `client_registered` | New client signs up | Welcome email with getting started guide |
| `service_requested` | Client submits request | Confirmation with expected timeline |
| `service_completed` | Work marked complete | Completion notice with next steps |
| `invoice_sent` | Invoice emailed | Payment reminder after 7 days |
| `invoice_overdue` | Past due date | Escalating reminders |
| `payment_received` | Payment confirmed | Thank you receipt |
| `document_uploaded` | Client uploads file | Acknowledgment email |
| `query_raised` | Accountant asks question | Notification to respond |
| `birthday` | Client's birthday | Birthday greeting |
| `anniversary` | 1 year as client | Loyalty appreciation |
| `inactivity` | No activity for X days | Re-engagement email |
| `custom` | Via API webhook | Custom integrations |

---

## Competitive Advantages

### Why Choose Accountant CRM?

| Advantage | Description |
|-----------|-------------|
| **Australian-First Design** | Built for AU accounting: GST, TFN, ABN, SMSF, ATO requirements |
| **Multi-Tenant SaaS** | Practices get isolated data with shared infrastructure efficiency |
| **Modern Technology** | React frontend, Python backend, cloud-native architecture |
| **Stripe Integration** | Accept payments instantly, no manual reconciliation |
| **Email Automation** | Set it and forget it - 12 trigger types |
| **Custom Forms** | Build any form without coding - conditional logic included |
| **White-Label Ready** | Practices can brand as their own |
| **API Access** | Integrate with existing tools (Premium+) |
| **Competitive Pricing** | Starts at $49/month - cheaper than legacy solutions |

### Competitor Comparison

| Feature | Accountant CRM | Competitor A | Competitor B |
|---------|:--------------:|:------------:|:------------:|
| Australian Tax Focus | ✅ | ❌ | ✅ |
| Multi-Tenant | ✅ | ❌ | ✅ |
| Custom Forms | ✅ | ⚠️ Limited | ❌ |
| Stripe Payments | ✅ | ❌ | ✅ |
| Email Automation | ✅ | ⚠️ Basic | ❌ |
| Starting Price | $49 | $99 | $79 |
| White-Label | ✅ | ❌ | ⚠️ Extra cost |
| Modern UI | ✅ | ❌ | ⚠️ |

---

## Integration Capabilities

### Current Integrations

| Integration | Type | Description |
|-------------|------|-------------|
| **Stripe** | Payment | Online payments, webhooks, automatic reconciliation |
| **Microsoft Graph** | Email | Send emails via Office 365 |
| **Azure Blob Storage** | Storage | Secure document storage |

### API Access (Premium+)

RESTful API available for custom integrations:

```
Base URL: https://api.accountantcrm.com/v1

Authentication: JWT Bearer Token

Endpoints:
- GET    /clients         - List clients
- POST   /clients         - Create client
- GET    /requests        - List service requests
- POST   /requests        - Create request
- GET    /invoices        - List invoices
- POST   /invoices        - Create invoice
- ...and more
```

### Planned Integrations (Roadmap)

| Integration | Timeline | Description |
|-------------|----------|-------------|
| Xero | Q2 2026 | Two-way sync with Xero accounting |
| MYOB | Q3 2026 | Integration with MYOB |
| ATO Portal | Q4 2026 | Direct lodgement capability |
| Zapier | Q2 2026 | Connect to 5000+ apps |

---

## Security & Compliance

### Security Features

| Feature | Description |
|---------|-------------|
| **Encryption at Rest** | All data encrypted in database |
| **Encryption in Transit** | TLS 1.3 for all connections |
| **JWT Authentication** | Secure token-based auth |
| **2FA Support** | Email OTP verification |
| **Role-Based Access** | Granular permissions |
| **Audit Logging** | Complete activity trail |
| **Session Management** | Token expiry and refresh |
| **Secure File Storage** | Azure Blob with SAS tokens |

### Compliance

| Standard | Status |
|----------|--------|
| **Privacy Act 1988** | ✅ Compliant |
| **Australian Privacy Principles** | ✅ Compliant |
| **GDPR** | ✅ Ready (for EU clients) |
| **PCI DSS** | ✅ Via Stripe (Level 1) |
| **SOC 2** | 🔄 In Progress |

### Data Residency

- Primary data center: **Australia East (Sydney)**
- Backup data center: **Australia Southeast (Melbourne)**
- All client data remains in Australia

---

## Technical Specifications

### Platform Architecture

| Component | Technology |
|-----------|------------|
| **Frontend** | React 18, TypeScript, Tailwind CSS |
| **Backend** | Python 3.11, Flask |
| **Database** | PostgreSQL 15 |
| **File Storage** | Azure Blob Storage |
| **Email** | Microsoft Graph API |
| **Payments** | Stripe |
| **Hosting** | Azure App Service / Docker |

### Performance

| Metric | Target |
|--------|--------|
| Page Load Time | < 2 seconds |
| API Response Time | < 200ms (p95) |
| Uptime SLA | 99.9% (Enterprise) |
| Data Backup | Every 6 hours |
| Disaster Recovery | < 4 hours RTO |

### Browser Support

| Browser | Minimum Version |
|---------|-----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |
| Mobile Safari | iOS 14+ |
| Chrome Mobile | Android 10+ |

---

## Frequently Asked Questions

### General

**Q: Is this suitable for practices outside Australia?**
A: The platform is optimized for Australian accounting (GST, TFN, etc.) but can be used internationally. Some features like tax calculations would need customization.

**Q: How long does onboarding take?**
A: Most practices are fully operational within 1-2 days. We provide onboarding support to import existing clients and configure services.

**Q: Can I import my existing client data?**
A: Yes, we support CSV import for clients. Contact support for bulk migration assistance.

---

### Pricing & Billing

**Q: Is there a free trial?**
A: Yes, 14-day free trial on all plans. No credit card required.

**Q: Can I change plans later?**
A: Yes, upgrade or downgrade anytime. Changes are prorated.

**Q: What payment methods do you accept?**
A: Credit card (Visa, Mastercard, Amex) via Stripe. Enterprise plans can pay by invoice.

**Q: Are there any setup fees?**
A: No setup fees for Starter, Standard, and Premium plans. Enterprise plans may have implementation fees depending on requirements.

---

### Features

**Q: Can my clients pay invoices online?**
A: Yes, with Standard plan and above. Clients receive a secure Stripe checkout link.

**Q: How many email templates can I create?**
A: Unlimited templates on all plans.

**Q: Can I customize the forms?**
A: Yes, the form builder supports 11 question types with conditional logic. Create any form you need.

**Q: Is there a mobile app?**
A: The web application is fully responsive and works on mobile browsers. Native apps are on the roadmap.

---

### Security

**Q: Where is my data stored?**
A: All data is stored in Australian data centers (Azure Australia East).

**Q: Is client data backed up?**
A: Yes, automated backups every 6 hours with 30-day retention.

**Q: Can other practices see my data?**
A: No, the multi-tenant architecture ensures complete data isolation between practices.

---

### Support

**Q: What support is included?**
A:
- Starter: Email support (48hr response)
- Standard: Priority email (24hr response)
- Premium: Email + Phone (same day)
- Enterprise: Dedicated account manager

**Q: Do you offer training?**
A: Yes, we provide onboarding training sessions. Enterprise plans include ongoing training.

---

## Glossary

| Term | Definition |
|------|------------|
| **Tenant** | An accounting practice using the platform |
| **Practice Owner** | The admin user who manages a practice |
| **Service Request** | A client's request for a specific service |
| **Query** | A question/message between accountant and client |
| **Form Response** | Client's submitted answers to a form |
| **Automation Trigger** | An event that initiates an automated email |
| **SAS Token** | Secure time-limited URL for document access |
| **Webhook** | Automated notification from Stripe about payments |
| **Multi-tenant** | Architecture where multiple practices share infrastructure but have isolated data |
| **White-label** | Ability to brand the platform as your own |

---

## Contact Information

### Sales Inquiries
- **Email:** sales@accountantcrm.com
- **Phone:** 1300 XXX XXX

### Support
- **Email:** support@accountantcrm.com
- **Help Center:** help.accountantcrm.com

### Partnership Opportunities
- **Email:** partners@accountantcrm.com

---

*Document Version: 1.0 | January 2026*
*This document is confidential and intended for internal business development use.*
