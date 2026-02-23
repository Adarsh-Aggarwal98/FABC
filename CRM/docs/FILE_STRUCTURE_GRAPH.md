# Sharat CRM - Complete File Structure Graph

## Root Directory Structure

```
E:\sharat crm\
│
├── backend/                                    # Flask Backend
│   ├── app/                                   # Main Application
│   │   ├── __init__.py                       # App factory, blueprint registration
│   │   ├── config.py                         # Configuration (Dev/Test/Prod)
│   │   ├── extensions.py                     # Flask extensions (SQLAlchemy, JWT, CORS)
│   │   │
│   │   ├── common/                           # Shared Components
│   │   │   ├── __init__.py
│   │   │   ├── repository.py                 # BaseRepository[T] generic CRUD
│   │   │   ├── usecase.py                    # BaseUseCase, UseCaseResult
│   │   │   ├── service.py                    # BaseService, BaseDomainService
│   │   │   ├── decorators.py                 # @admin_required, @accountant_required
│   │   │   └── responses.py                  # success_response(), error_response()
│   │   │
│   │   └── modules/                          # Feature Modules (16 total)
│   │       │
│   │       ├── user/                         # User Management [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: auth_bp, users_bp
│   │       │   ├── models/                  # Split models
│   │       │   │   ├── __init__.py          # Exports all models
│   │       │   │   ├── user.py              # User model
│   │       │   │   ├── role.py              # Role model
│   │       │   │   ├── otp.py               # OTP model
│   │       │   │   └── user_note.py         # UserNote model
│   │       │   ├── repositories/            # Data Access
│   │       │   │   └── user_repository.py
│   │       │   ├── usecases/                # Business Logic
│   │       │   │   ├── auth/                # Login, verify, password reset
│   │       │   │   └── users/               # User CRUD
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   ├── routes/                  # API endpoints
│   │       │   │   ├── auth_routes.py       # /auth/*
│   │       │   │   └── user_routes.py       # /users/*
│   │       │   ├── models.py                # Backward compat re-export
│   │       │   ├── routes.py                # Backward compat re-export
│   │       │   └── schemas.py               # Backward compat re-export
│   │       │
│   │       ├── company/                      # Company/Multi-tenant [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: companies_bp
│   │       │   ├── models/                  # Split models
│   │       │   │   ├── company.py           # Company model
│   │       │   │   └── smtp_config.py       # SMTPConfig model
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   ├── routes/                  # API endpoints
│   │       │   ├── models.py                # Backward compat re-export
│   │       │   └── schemas.py               # Backward compat re-export
│   │       │
│   │       ├── services/                     # Service Requests [REFACTORED STRUCTURE]
│   │       │   ├── __init__.py              # Blueprints: services_bp, requests_bp,
│   │       │   │                            #   workflow_bp, renewals_bp, status_bp,
│   │       │   │                            #   invoices_bp
│   │       │   │
│   │       │   ├── models/                  # Split Models
│   │       │   │   ├── __init__.py          # Exports all models
│   │       │   │   ├── service.py           # Service catalog model
│   │       │   │   ├── service_request.py   # ServiceRequest model (main entity)
│   │       │   │   ├── query.py             # Query/Message model
│   │       │   │   ├── job_note.py          # Internal notes model
│   │       │   │   ├── invoice.py           # Invoice, InvoiceLineItem, InvoicePayment
│   │       │   │   ├── status.py            # Custom Status per company
│   │       │   │   ├── assignment_history.py # Assignment audit trail
│   │       │   │   └── request_audit_log.py  # Change history
│   │       │   │
│   │       │   ├── repositories/            # Data Access Layer
│   │       │   │   ├── __init__.py
│   │       │   │   ├── service_repository.py
│   │       │   │   ├── request_repository.py
│   │       │   │   ├── invoice_repository.py
│   │       │   │   └── status_repository.py
│   │       │   │
│   │       │   ├── usecases/                # Business Logic
│   │       │   │   ├── __init__.py          # Exports all use cases
│   │       │   │   ├── requests/            # Request-related
│   │       │   │   │   ├── create_request.py
│   │       │   │   │   ├── update_request.py
│   │       │   │   │   ├── assign_request.py
│   │       │   │   │   ├── update_status.py
│   │       │   │   │   └── ...
│   │       │   │   └── invoices/            # Invoice-related
│   │       │   │       ├── create_invoice.py
│   │       │   │       ├── send_invoice.py
│   │       │   │       └── ...
│   │       │   │
│   │       │   ├── services/                # Domain Services
│   │       │   │   ├── __init__.py
│   │       │   │   ├── workflow_service.py  # Status transitions, automations
│   │       │   │   ├── invoice_pdf_service.py # PDF generation (ReportLab)
│   │       │   │   └── renewal_service.py   # Annual renewal handling
│   │       │   │
│   │       │   ├── schemas/                 # Marshmallow Schemas
│   │       │   │   ├── __init__.py
│   │       │   │   ├── service_schemas.py
│   │       │   │   ├── request_schemas.py
│   │       │   │   ├── invoice_schemas.py
│   │       │   │   └── status_schemas.py
│   │       │   │
│   │       │   └── routes/                  # API Endpoints
│   │       │       ├── __init__.py          # Blueprint registration
│   │       │       ├── service_routes.py    # /services/*
│   │       │       ├── request_routes.py    # /requests/*
│   │       │       ├── invoice_routes.py    # /services/invoices/*
│   │       │       ├── status_routes.py     # /services/status/*
│   │       │       ├── workflow_routes.py   # /services/workflow/*
│   │       │       └── analytics_routes.py  # /requests/analytics/*
│   │       │
│   │       ├── documents/                    # Document Management [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: documents_bp
│   │       │   ├── models/                  # Split models
│   │       │   │   └── document.py          # Document model
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── services/                # DocumentService (upload/download)
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   ├── routes/                  # /documents/*
│   │       │   └── models.py                # Backward compat re-export
│   │       │
│   │       ├── forms/                        # Dynamic Forms [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: forms_bp
│   │       │   ├── models/                  # Split models
│   │       │   │   ├── form.py              # Form model
│   │       │   │   ├── form_question.py     # FormQuestion model
│   │       │   │   └── form_response.py     # FormResponse model
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   ├── routes/                  # /forms/*
│   │       │   └── models.py                # Backward compat re-export
│   │       │
│   │       ├── notifications/                # Email & Notifications [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: notifications_bp
│   │       │   ├── models/                  # Split models
│   │       │   │   ├── notification.py      # In-app notification
│   │       │   │   ├── email_template.py    # Email templates
│   │       │   │   ├── email_automation.py  # Automation triggers
│   │       │   │   └── scheduled_email.py   # Scheduled emails
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── services/                # NotificationService, EmailSender
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   ├── routes/                  # /notifications/*
│   │       │   └── models.py                # Backward compat re-export
│   │       │
│   │       ├── payments/                     # Stripe Payments [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: payments_bp
│   │       │   ├── models/                  # Split models
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── services/                # StripeService
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   └── routes/                  # /payments/*
│   │       │
│   │       ├── analytics/                    # Reports & Dashboards [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: analytics_bp
│   │       │   ├── models/                  # Split models
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── services/                # AnalyticsService
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   └── routes/                  # /analytics/*
│   │       │
│   │       ├── audit/                        # Audit Logging [REFACTORED]
│   │       │   ├── __init__.py              # Blueprint: audit_bp
│   │       │   ├── models/                  # Split models
│   │       │   │   ├── audit_log.py         # AuditLog model
│   │       │   │   └── access_log.py        # AccessLog model
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── services/                # AccessLogger, GeolocationService
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   ├── routes/                  # /audit/*
│   │       │   └── models.py                # Backward compat re-export
│   │       │
│   │       ├── client_entity/                # Client Business Entities [REFACTORED]
│   │       │   ├── __init__.py
│   │       │   ├── models/                  # Split models
│   │       │   │   └── client_entity.py     # ClientEntity model
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   └── routes/                  # /client-entities/*
│   │       │
│   │       ├── imports/                      # Data Import [REFACTORED]
│   │       │   ├── __init__.py
│   │       │   ├── models/                  # Split models
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── services/                # Import services
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   └── routes/                  # /imports/*
│   │       │
│   │       ├── search/                       # Global Search [REFACTORED]
│   │       │   ├── __init__.py
│   │       │   ├── services/                # SearchService
│   │       │   └── routes/                  # /search/*
│   │       │
│   │       ├── tags/                         # Tagging System [REFACTORED]
│   │       │   ├── __init__.py
│   │       │   ├── models/                  # Tag, user_tags association
│   │       │   ├── repositories/            # Data Access
│   │       │   ├── usecases/                # Business Logic
│   │       │   ├── schemas/                 # Marshmallow schemas
│   │       │   └── routes/                  # /tags/*
│   │       │
│   │       └── integrations/                 # Third-party Integrations
│   │           ├── __init__.py
│   │           ├── xero/                    # Xero Accounting
│   │           │   ├── __init__.py
│   │           │   ├── routes.py            # OAuth flow, sync
│   │           │   └── xero_service.py
│   │           ├── myob/                    # MYOB Accounting
│   │           │   ├── __init__.py
│   │           │   ├── routes.py
│   │           │   └── myob_service.py
│   │           ├── quickbooks/              # QuickBooks
│   │           │   ├── __init__.py
│   │           │   ├── routes.py
│   │           │   └── quickbooks_service.py
│   │           └── google_drive/            # Google Drive Storage
│   │               ├── __init__.py
│   │               ├── routes.py
│   │               └── google_drive_service.py
│   │
│   ├── tests/                                # Test Suite
│   │   ├── conftest.py                      # Fixtures (app, client, tokens, etc.)
│   │   ├── test_auth.py                     # Authentication tests
│   │   ├── test_users.py                    # User management tests
│   │   ├── test_companies.py                # Company tests
│   │   ├── test_services.py                 # Service request tests
│   │   ├── test_documents.py                # Document tests
│   │   ├── test_forms.py                    # Form tests
│   │   ├── test_notifications.py            # Notification tests
│   │   ├── test_analytics.py                # Analytics tests
│   │   └── test_invoices.py                 # Invoice tests
│   │
│   ├── sql_migrations/                       # Database Migrations
│   │   ├── create_db.sql                    # Initial schema
│   │   ├── upgrade_db_1.sql                 # Migration 1
│   │   ├── upgrade_db_2.sql                 # Migration 2
│   │   └── data_migration_1.py              # Data migration script
│   │
│   ├── uploads/                              # Local file storage (dev)
│   ├── .env                                  # Environment variables
│   ├── .env.example                          # Example environment
│   ├── requirements.txt                      # Python dependencies
│   ├── pytest.ini                            # Pytest configuration
│   ├── Dockerfile                            # Backend container
│   └── run.py                                # Development server entry
│
├── frontend/                                  # React Frontend
│   ├── src/
│   │   ├── main.jsx                         # React entry point
│   │   ├── App.jsx                          # Main app with routing
│   │   │
│   │   ├── components/                      # Reusable Components
│   │   │   ├── common/                      # Generic UI
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Badge.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── Table.jsx
│   │   │   │   └── ...
│   │   │   ├── layout/                      # Layout Components
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── Header.jsx
│   │   │   │   └── DashboardLayout.jsx
│   │   │   ├── features/                    # Feature-specific
│   │   │   │   ├── client-entities/
│   │   │   │   ├── notifications/
│   │   │   │   └── ...
│   │   │   └── kanban/                      # Kanban board
│   │   │       ├── KanbanBoard.jsx
│   │   │       ├── KanbanColumn.jsx
│   │   │       └── KanbanCard.jsx
│   │   │
│   │   ├── pages/                           # Page Components
│   │   │   ├── auth/                        # Login, Register
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Register.jsx
│   │   │   │   └── ForgotPassword.jsx
│   │   │   ├── dashboard/                   # Dashboard
│   │   │   │   └── Dashboard.jsx
│   │   │   ├── requests/                    # Service Requests
│   │   │   │   ├── RequestList.jsx
│   │   │   │   ├── RequestDetail.jsx
│   │   │   │   └── ...
│   │   │   ├── services/                    # Services
│   │   │   │   ├── ServiceList.jsx
│   │   │   │   └── NewServiceRequest.jsx
│   │   │   ├── users/                       # User Management
│   │   │   │   ├── UserList.jsx
│   │   │   │   └── UserProfile.jsx
│   │   │   ├── settings/                    # Settings
│   │   │   │   ├── CompanySettings.jsx
│   │   │   │   └── StatusSettings.jsx
│   │   │   └── client-entities/             # Client Entities
│   │   │       └── ClientEntityList.jsx
│   │   │
│   │   ├── services/                        # API Client
│   │   │   └── api.js                       # Axios instance, API calls
│   │   │
│   │   ├── contexts/                        # React Context
│   │   │   ├── AuthContext.jsx
│   │   │   └── NotificationContext.jsx
│   │   │
│   │   ├── hooks/                           # Custom Hooks
│   │   │   ├── useAuth.js
│   │   │   └── useApi.js
│   │   │
│   │   └── utils/                           # Utility Functions
│   │       ├── formatters.js
│   │       └── validators.js
│   │
│   ├── public/                               # Static Assets
│   ├── index.html                            # HTML entry
│   ├── vite.config.js                        # Vite configuration
│   ├── tailwind.config.js                    # Tailwind CSS config
│   ├── package.json                          # NPM dependencies
│   └── Dockerfile                            # Frontend container
│
├── docs/                                      # Documentation
│   ├── ARCHITECTURE_DOCUMENTATION.md         # Main docs (this file)
│   ├── FILE_STRUCTURE_GRAPH.md              # File structure (this file)
│   ├── BUSINESS_DEVELOPMENT_GUIDE.md        # Business guide
│   ├── KANBAN_FEATURE.md                    # Kanban feature docs
│   └── CLIENT_ENTITY_FEATURE.md             # Client entity docs
│
├── docker-compose.yml                         # Docker Compose (Linux/Mac)
├── docker-compose.windows.yml                 # Docker Compose (Windows)
├── deploy.sh                                  # Deployment script
└── README.md                                  # Project README
```

## Module Dependencies Graph

```
                    ┌───────────────────────────┐
                    │         app/__init__.py   │
                    │    (Blueprint Registration)│
                    └───────────────┬───────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │   auth_bp     │      │  services_bp  │      │  analytics_bp │
    │   /api/auth   │      │  /api/services│      │  /api/analytics│
    └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │   user/       │      │   services/   │      │   analytics/  │
    │   models      │◄─────│   models      │◄─────│   services    │
    └───────────────┘      └───────────────┘      └───────────────┘
            │                       │
            │              ┌────────┼────────┐
            │              │        │        │
            ▼              ▼        ▼        ▼
    ┌───────────────┐  ┌────────┐┌────────┐┌────────┐
    │   company/    │  │requests││invoices││workflow│
    │   models      │  │_bp     ││_bp     ││_bp     │
    └───────────────┘  └────────┘└────────┘└────────┘
            │
            ▼
    ┌───────────────┐
    │ notifications/│
    │   services    │
    └───────────────┘
```

## Data Flow Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│    Frontend     │      │     Backend     │      │    Database     │
│    (React)      │◄────►│    (Flask)      │◄────►│  (PostgreSQL)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │                        │
        │ HTTP/REST              │                        │
        │                        ▼                        │
        │               ┌─────────────────┐               │
        │               │   JWT Auth      │               │
        │               │   Middleware    │               │
        │               └─────────────────┘               │
        │                        │                        │
        │                        ▼                        │
        │               ┌─────────────────┐               │
        │               │     Routes      │               │
        │               │  (Controllers)  │               │
        │               └─────────────────┘               │
        │                        │                        │
        │                        ▼                        │
        │               ┌─────────────────┐               │
        │               │    Schemas      │               │
        │               │  (Validation)   │               │
        │               └─────────────────┘               │
        │                        │                        │
        │                        ▼                        │
        │               ┌─────────────────┐               │
        │               │   Use Cases     │               │
        │               │ (Business Logic)│               │
        │               └─────────────────┘               │
        │                        │                        │
        │                        ▼                        │
        │               ┌─────────────────┐               │
        │               │  Repositories   │               │
        │               │  (Data Access)  │               │
        │               └─────────────────┘               │
        │                        │                        │
        │                        ▼                        │
        │               ┌─────────────────┐               │
        │               │   SQLAlchemy    │──────────────►│
        │               │     Models      │               │
        │               └─────────────────┘               │
        │                                                 │
        ▼                                                 │
┌─────────────────┐                              ┌────────┴────────┐
│  External APIs  │                              │   File Storage  │
│  - Stripe       │                              │   - Azure Blob  │
│  - Xero         │                              │   - Google Drive│
│  - SMTP         │                              │   - Local       │
└─────────────────┘                              └─────────────────┘
```

## Key Files Quick Reference

| Purpose | File |
|---------|------|
| App Entry | `backend/app/__init__.py` |
| Config | `backend/app/config.py` |
| Environment | `backend/.env` |
| Base Repository | `backend/app/common/repository.py` |
| Base Use Case | `backend/app/common/usecase.py` |
| Auth Routes | `backend/app/modules/user/routes/auth_routes.py` |
| User Routes | `backend/app/modules/user/routes/user_routes.py` |
| Request Routes | `backend/app/modules/services/routes/request_routes.py` |
| Invoice Routes | `backend/app/modules/services/routes/invoice_routes.py` |
| Email Service | `backend/app/modules/notifications/services/email_service.py` |
| Notification Service | `backend/app/modules/notifications/services/notification_service.py` |
| Document Upload | `backend/app/modules/documents/services/document_service.py` |
| Tests Config | `backend/tests/conftest.py` |
| Frontend Entry | `frontend/src/main.jsx` |
| API Client | `frontend/src/services/api.js` |
| Main Routes | `frontend/src/App.jsx` |

## Architecture Pattern

All 14 backend modules follow the Clean Architecture pattern:

```
Request → Routes → Schemas → Use Cases → Repositories → Models → Database
                                ↓
                            Services (domain logic, external APIs)
```

Each layer has a single responsibility:
- **Routes**: HTTP handling only, no business logic
- **Schemas**: Request/response validation (Marshmallow 4.x)
- **Use Cases**: Business logic orchestration, returns UseCaseResult
- **Repositories**: Data access abstraction (extends BaseRepository[T])
- **Services**: Complex domain operations, external integrations
- **Models**: SQLAlchemy ORM definitions with to_dict() serialization
