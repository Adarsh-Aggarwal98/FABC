# Sharat CRM - Complete Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Schema](#database-schema)
7. [API Documentation](#api-documentation)
8. [Authentication Flow](#authentication-flow)
9. [Module Details](#module-details)
10. [Deployment Guide](#deployment-guide)

---

## Overview

Sharat CRM is a comprehensive Customer Relationship Management system designed for accounting firms. It provides:
- **Multi-tenant Architecture**: Each accounting firm has isolated data
- **Service Request Management**: Track client requests from submission to completion
- **Document Management**: Store and organize client documents (Azure Blob, Google Drive)
- **Invoice & Payment Processing**: Generate invoices and process payments (Stripe)
- **Email Automation**: Automated notifications and bulk email campaigns
- **Accounting Integrations**: Connect with Xero, MYOB, QuickBooks
- **Role-Based Access Control**: Super Admin, Admin, Accountant, User roles

---

## Technology Stack

### Backend
- **Framework**: Flask 2.x (Python 3.11+)
- **Database**: PostgreSQL 15+ / SQLite (development)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-JWT-Extended (JWT tokens)
- **Validation**: Marshmallow 4.x
- **Email**: SMTP / Microsoft Graph API
- **Storage**: Azure Blob Storage / Google Drive
- **Payments**: Stripe

### Frontend
- **Framework**: React 18+ with Vite
- **State Management**: React Context + Custom Hooks
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Forms**: React Hook Form

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions (planned)
- **Hosting**: Azure / AWS / Custom VPS

---

## Project Structure

```
sharat-crm/
├── backend/                        # Flask Backend Application
│   ├── app/                       # Main Application Package
│   │   ├── __init__.py           # App factory & Blueprint registration
│   │   ├── config.py             # Configuration classes
│   │   ├── extensions.py         # SQLAlchemy, JWT, CORS initialization
│   │   │
│   │   ├── common/               # Shared utilities & base classes
│   │   │   ├── repository.py     # BaseRepository[T] - Generic CRUD
│   │   │   ├── usecase.py        # BaseUseCase, UseCaseResult
│   │   │   ├── service.py        # BaseService, BaseDomainService
│   │   │   ├── decorators.py     # Auth decorators (@admin_required, etc)
│   │   │   └── responses.py      # Standard API responses
│   │   │
│   │   └── modules/              # Feature Modules
│   │       ├── user/             # User Management (flat structure)
│   │       ├── company/          # Company/Multi-tenant
│   │       ├── services/         # Service Requests (refactored structure)
│   │       ├── documents/        # Document Management
│   │       ├── forms/            # Dynamic Forms
│   │       ├── notifications/    # Email & In-app Notifications
│   │       ├── payments/         # Stripe Payments
│   │       ├── analytics/        # Reports & Dashboards
│   │       ├── audit/            # Audit Logging
│   │       └── integrations/     # Xero, MYOB, QuickBooks, etc.
│   │
│   ├── tests/                    # Unit & Integration Tests
│   ├── sql_migrations/           # Database Migrations
│   ├── requirements.txt          # Python Dependencies
│   └── Dockerfile               # Backend Container
│
├── frontend/                      # React Frontend Application
│   ├── src/
│   │   ├── components/           # Reusable UI Components
│   │   ├── pages/               # Page Components
│   │   ├── services/            # API Client
│   │   ├── contexts/            # React Context Providers
│   │   ├── hooks/               # Custom React Hooks
│   │   └── utils/               # Utility Functions
│   │
│   ├── public/                   # Static Assets
│   └── Dockerfile               # Frontend Container
│
├── docs/                         # Documentation
├── docker-compose.yml           # Docker Compose (Linux/Mac)
├── docker-compose.windows.yml   # Docker Compose (Windows)
└── README.md                    # Project README
```

---

## Backend Architecture

### Layer Architecture

The backend follows a **Clean Architecture** pattern with distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│  ROUTES (Controllers)                                        │
│  - Parse HTTP requests                                       │
│  - Validate input with schemas                               │
│  - Call use cases                                            │
│  - Format HTTP responses                                     │
│  - NO business logic                                         │
├─────────────────────────────────────────────────────────────┤
│  USE CASES (Application Logic)                               │
│  - Orchestrate repositories and services                     │
│  - Contain business rules                                    │
│  - Handle transactions                                       │
│  - Return UseCaseResult                                      │
├─────────────────────────────────────────────────────────────┤
│  SERVICES (Domain Logic)                                     │
│  - Complex domain operations                                 │
│  - External integrations                                     │
│  - Cross-entity operations                                   │
├─────────────────────────────────────────────────────────────┤
│  REPOSITORIES (Data Access)                                  │
│  - CRUD operations                                           │
│  - Query building                                            │
│  - Database abstraction                                      │
├─────────────────────────────────────────────────────────────┤
│  MODELS (Entities)                                           │
│  - SQLAlchemy ORM definitions                                │
│  - Relationships                                             │
│  - Serialization (to_dict)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure (Clean Architecture)

**All 14 modules** now follow the clean architecture pattern:

```
app/modules/{module}/
├── __init__.py                 # Blueprint registration
├── models/                     # SQLAlchemy Models
│   ├── __init__.py            # Export all models (backward-compatible)
│   ├── {entity}.py            # One model per file
│   └── ...
├── repositories/               # Data Access Layer
│   ├── __init__.py
│   └── {entity}_repository.py
├── usecases/                   # Business Logic
│   ├── __init__.py
│   └── {action}_{entity}.py
├── services/                   # Domain Services
│   ├── __init__.py
│   └── {domain}_service.py
├── schemas/                    # Marshmallow Schemas
│   ├── __init__.py
│   └── {entity}_schemas.py
└── routes/                     # API Endpoints
    ├── __init__.py
    └── {resource}_routes.py
```

### Refactored Modules

All backend modules have been refactored to this structure:

| Module | Description |
|--------|-------------|
| `user` | User authentication, profiles, invitations |
| `company` | Multi-tenant company management |
| `services` | Service catalog and requests |
| `documents` | File upload/download with Azure/Google Drive |
| `forms` | Dynamic form builder and responses |
| `notifications` | Email templates, automations, in-app notifications |
| `payments` | Stripe payment integration |
| `analytics` | Reports and dashboards |
| `audit` | Audit logging and access tracking |
| `client_entity` | Client business entity records |
| `imports` | Data import functionality |
| `integrations` | Xero, MYOB, QuickBooks, Google Drive |
| `search` | Global search functionality |
| `tags` | Tagging system for clients |

### Backward Compatibility

Each module maintains backward compatibility through re-export shim files:
- `models.py` re-exports from `models/`
- `routes.py` re-exports from `routes/`
- `schemas.py` re-exports from `schemas/`

This allows existing imports to continue working while new code uses the clean architecture paths.

---

## Database Schema

### Core Entities

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    companies     │────<│      users       │────<│  notifications   │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK, UUID)    │     │ id (PK, UUID)    │     │ id (PK, INT)     │
│ name             │     │ email            │     │ user_id (FK)     │
│ abn              │     │ password_hash    │     │ title            │
│ plan_type        │     │ role_id (FK)     │     │ message          │
│ is_active        │     │ company_id (FK)  │     │ is_read          │
└──────────────────┘     │ is_verified      │     └──────────────────┘
                         └──────────────────┘
                                  │
                                  ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    services      │────<│ service_requests │────<│     queries      │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK, INT)     │     │ id (PK, UUID)    │     │ id (PK, INT)     │
│ name             │     │ request_number   │     │ request_id (FK)  │
│ category         │     │ user_id (FK)     │     │ user_id (FK)     │
│ base_price       │     │ service_id (FK)  │     │ message          │
│ is_default       │     │ status           │     │ is_client_visible│
└──────────────────┘     │ assigned_to (FK) │     └──────────────────┘
                         │ invoice_raised   │
                         │ invoice_paid     │
                         └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    documents     │
                         ├──────────────────┤
                         │ id (PK, UUID)    │
                         │ request_id (FK)  │
                         │ original_name    │
                         │ blob_name        │
                         │ storage_type     │
                         └──────────────────┘
```

### Roles Hierarchy

```
┌─────────────────┐
│   super_admin   │  ← Platform administrator (all companies)
├─────────────────┤
│     admin       │  ← Company owner/administrator
├─────────────────┤
│   accountant    │  ← Staff member (assigned to requests)
├─────────────────┤
│      user       │  ← Client (end user)
└─────────────────┘
```

---

## API Documentation

### Base URL
- **Development**: `http://localhost:5001/api`
- **Production**: `https://api.flownetics.smartrootstutoring.com.au/api`

### Authentication

All protected endpoints require JWT token:
```
Authorization: Bearer <access_token>
```

### Endpoint Categories

| Module | Prefix | Description |
|--------|--------|-------------|
| Auth | `/auth` | Login, Register, Password Reset |
| Users | `/users` | User CRUD, Profile, Invitations |
| Companies | `/companies` | Company Management |
| Services | `/services` | Service Catalog |
| Requests | `/requests` | Service Requests |
| Documents | `/documents` | File Upload/Download |
| Forms | `/forms` | Dynamic Forms |
| Notifications | `/notifications` | Email Templates, Automations |
| Payments | `/payments` | Stripe Integration |
| Analytics | `/analytics` | Reports, Dashboards |

### Key Endpoints

```
# Authentication
POST   /api/auth/login              Login with email/password
POST   /api/auth/verify-otp         Verify 2FA OTP
POST   /api/auth/register           Register new company
POST   /api/auth/forgot-password    Request password reset
GET    /api/auth/me                 Get current user profile

# Service Requests
GET    /api/requests                List requests (filtered)
POST   /api/requests                Create new request
GET    /api/requests/:id            Get request details
PATCH  /api/requests/:id            Update request
POST   /api/requests/:id/assign     Assign to accountant
PATCH  /api/requests/:id/status     Update status
POST   /api/requests/:id/queries    Add message/query

# Documents
POST   /api/documents               Upload document
GET    /api/documents               List documents
GET    /api/documents/:id/download  Get download URL
DELETE /api/documents/:id           Delete document

# Invoices
GET    /api/services/invoices       List invoices
POST   /api/services/invoices       Create invoice
GET    /api/services/invoices/:id   Get invoice
POST   /api/services/invoices/:id/send    Send to client
```

---

## Authentication Flow

### Login Flow (2FA Enabled)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │   API    │     │ Database │     │  Email   │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                 │                 │                 │
     │ POST /login     │                 │                 │
     │ (email, pass)   │                 │                 │
     │────────────────>│                 │                 │
     │                 │ Validate        │                 │
     │                 │ credentials     │                 │
     │                 │────────────────>│                 │
     │                 │<────────────────│                 │
     │                 │                 │                 │
     │                 │ Generate OTP    │                 │
     │                 │────────────────>│                 │
     │                 │                 │                 │
     │                 │ Send OTP email  │                 │
     │                 │─────────────────────────────────>│
     │                 │                 │                 │
     │<────────────────│                 │                 │
     │ {requires_otp}  │                 │                 │
     │                 │                 │                 │
     │ POST /verify-otp│                 │                 │
     │ (email, otp)    │                 │                 │
     │────────────────>│                 │                 │
     │                 │ Verify OTP      │                 │
     │                 │────────────────>│                 │
     │                 │<────────────────│                 │
     │                 │                 │                 │
     │                 │ Generate JWT    │                 │
     │                 │                 │                 │
     │<────────────────│                 │                 │
     │ {access_token}  │                 │                 │
```

### Login Flow (2FA Disabled)

```
Client -> POST /login -> Validate -> Return JWT immediately
```

---

## Module Details

### 1. User Module (`app/modules/user/`)

Handles user authentication, profile management, and invitations.

**Models:**
- `User` - Core user entity
- `Role` - User roles (super_admin, admin, accountant, user)
- `OTP` - One-time passwords for 2FA
- `PasswordReset` - Password reset tokens
- `UserNote` - Internal notes on clients

**Key Features:**
- JWT-based authentication with refresh tokens
- 2FA via email OTP
- User invitation workflow
- Password complexity validation
- Profile management

### 2. Services Module (`app/modules/services/`)

Core module for service request management. **Fully refactored** with clean architecture.

**Models:**
- `Service` - Service catalog items
- `ServiceRequest` - Client service requests
- `Query` - Messages/queries on requests
- `JobNote` - Internal notes on requests
- `Invoice` - Generated invoices
- `InvoiceLineItem` - Invoice line items
- `InvoicePayment` - Payment records
- `Status` - Custom statuses per company
- `AssignmentHistory` - Request assignment audit
- `RequestAuditLog` - Change history

**Use Cases:**
- `CreateRequestUseCase`
- `AssignRequestUseCase`
- `UpdateStatusUseCase`
- `CreateInvoiceUseCase`
- etc.

### 3. Documents Module (`app/modules/documents/`)

Handles file uploads and storage.

**Storage Backends:**
- Azure Blob Storage (primary)
- Google Drive
- Local filesystem (fallback)

**Features:**
- Secure download URLs with expiry
- Category-based organization
- MIME type detection
- Malicious file detection

### 4. Forms Module (`app/modules/forms/`)

Dynamic form builder for client onboarding and service-specific questionnaires.

**Features:**
- Multiple question types (text, select, file, etc.)
- Conditional logic
- Form versioning (draft/published/archived)
- Form cloning

### 5. Notifications Module (`app/modules/notifications/`)

Email and in-app notification system.

**Features:**
- In-app notifications
- Email templates (customizable per company)
- Bulk email campaigns
- Scheduled emails
- Email automation triggers

### 6. Payments Module (`app/modules/payments/`)

Stripe payment integration.

**Features:**
- Checkout sessions
- Payment intents
- Webhook handling
- Payment links
- Saved payment methods

---

## Environment Variables

```bash
# Required
FLASK_ENV=production
SECRET_KEY=<random-secure-key>
JWT_SECRET_KEY=<random-secure-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Frontend URL (for email links)
FRONTEND_URL=https://flownetics.smartrootstutoring.com.au

# Email (SMTP)
SYSTEM_SMTP_ENABLED=true
SYSTEM_SMTP_HOST=smtp.gmail.com
SYSTEM_SMTP_PORT=587
SYSTEM_SMTP_USERNAME=<email>
SYSTEM_SMTP_PASSWORD=<app-password>
SYSTEM_SMTP_SENDER_EMAIL=<email>
SYSTEM_SMTP_SENDER_NAME=Flownetics

# Storage (Azure)
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_STORAGE_CONTAINER=documents

# Optional - Stripe
STRIPE_SECRET_KEY=<stripe-key>
STRIPE_PUBLISHABLE_KEY=<stripe-pub-key>
STRIPE_WEBHOOK_SECRET=<webhook-secret>

# Optional - Accounting Integrations
XERO_CLIENT_ID=
XERO_CLIENT_SECRET=
MYOB_CLIENT_ID=
MYOB_CLIENT_SECRET=
QUICKBOOKS_CLIENT_ID=
QUICKBOOKS_CLIENT_SECRET=
```

---

## Deployment Guide

### Docker Compose (Windows)

```bash
# Start all services
docker-compose -f docker-compose.windows.yml up -d

# View logs
docker-compose -f docker-compose.windows.yml logs -f

# Rebuild after changes
docker-compose -f docker-compose.windows.yml up -d --build
```

### Manual Deployment

```bash
# Backend
cd backend
pip install -r requirements.txt
flask db upgrade
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app('production')"

# Frontend
cd frontend
npm install
npm run build
# Serve dist/ folder with nginx
```

---

## Test Coverage

Current test status: **171 tests passing** (all tests pass)

Run tests:
```bash
cd backend
python -m pytest tests/ -v
```

### Test Categories
- `test_auth.py` - Authentication and 2FA tests
- `test_users.py` - User management tests
- `test_companies.py` - Company/multi-tenant tests
- `test_services.py` - Service request workflow tests
- `test_forms.py` - Dynamic form and response tests
- `test_documents.py` - File upload/download tests
- `test_notifications.py` - Email automation tests
- `test_invoices.py` - Invoice generation tests
- `test_analytics.py` - Dashboard metrics tests

---

## Support

- **Login URL**: https://flownetics.smartrootstutoring.com.au
- **API Base**: https://api.flownetics.smartrootstutoring.com.au/api
- **Issues**: Report via GitHub Issues
