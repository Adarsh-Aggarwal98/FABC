# Accountant CRM
a
A comprehensive CRM system for accountant practices with multi-tenant company management, role-based access, service request management, 2FA authentication, Stripe payments, and custom form builder.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Default Login Credentials](#default-login-credentials)
- [Manual Setup (Without Docker)](#manual-setup-without-docker)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)

---

## Features

- **Multi-Tenant Architecture**: Manage multiple accounting practices (companies)
- **Role-Based Access Control**: Super Admin, Admin, Accountant, and User roles
- **Company Management**: Create practices with owners, manage users per company
- **User Management**: Invite users via email with auto-generated passwords
- **Two-Factor Authentication**: Email OTP verification
- **Service Request System**: Multi-service selection, status tracking, assignment
- **Custom Form Builder**: Google Forms-like interface with conditional logic
- **Query System**: In-app messaging between users and accountants
- **Invoice & Payments**: Stripe integration, payment links, GST calculation
- **Document Storage**: Azure Blob Storage / Local storage support
- **Email Notifications**: Automated emails, bulk email, scheduled emails
- **Analytics Dashboard**: Revenue stats, workload reports, bottleneck analysis

---

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Adarsh-Aggarwal98/Jaypee_crm.git
cd Jaypee_crm

# Start all services (backend, frontend, database)
docker-compose up --build

# Wait for services to initialize (about 60 seconds)
# The database will be seeded automatically with default users and data
```

**Access the application:**
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5000/api |
| API Health Check | http://localhost:5000/api/health |

**Stop the services:**
```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop and remove database volume (fresh start)
```

### Option 2: Manual Setup

See [Manual Setup](#manual-setup-without-docker) section below.

---

## Default Login Credentials

After running the application, use these credentials to log in:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| **Super Admin** | admin@example.com | Admin@123 | Full system access, can create companies |
| **Practice Admin** | practiceadmin@example.com | Practice@123 | Admin of "Demo Accounting Practice" |
| **Accountant** | accountant@example.com | Accountant@123 | Works on assigned requests |
| **Demo Client** | demo@example.com | Demo@123 | Sample client with demo requests |
| **Test Client** | client@example.com | Client@123 | Another test client user |

### Pointer Accounting Practice

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| **Practice Admin** | admin@pointeraccounting.com.au | Pointer@123 | Owner of "Pointer Accounting" |
| **Accountant** | accountant@pointeraccounting.com.au | Pointer@123 | Accountant at Pointer Accounting |

**Sample Companies:**

**1. Demo Accounting Practice**
- Practice Admin is the owner
- Accountant and Clients are members
- Pre-loaded with sample service requests

**2. Pointer Accounting**
- Pointer Admin is the owner
- Includes one accountant

---

## Pre-Loaded Demo Data

The application comes with:

### Services
- Individual Tax Return ($350)
- Business Activity Statement - BAS ($150)
- Investment Rental Property ($200)
- SMSF Super Setup ($1,500)
- Company Incorporation ($800)

### Forms
- Individual Tax Return Information Form
- BAS Information Form
- Rental Property Information Form
- SMSF Setup Form (with conditional logic)
- Company Incorporation Form (multi-section, repeatable fields)
- SMSF Annual Compliance Questionnaire
- Company Annual Compliance Questionnaire

### Sample Requests (for demo@example.com)
- Completed Tax Return (with message history)
- Processing BAS
- Query Raised - Rental Property
- Assigned - SMSF Setup
- Pending - Company Incorporation

---

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file from example)
cp .env.example .env
# Edit .env with your database credentials

# Initialize database and seed data
flask db upgrade           # Run migrations
flask init-db              # Create default roles and users
flask create-sample-services  # Create services and forms
flask create-demo-data     # Create demo requests

# Start the backend server
python run.py
# Backend will be available at http://localhost:5000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend will be available at http://localhost:5173
```

### Database Setup (PostgreSQL)

```sql
-- Create database
CREATE DATABASE accountant_crm;

-- Create user (optional)
CREATE USER crm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE accountant_crm TO crm_user;
```

---

## Flask CLI Commands

```bash
# Initialize database with default roles and users
flask init-db

# Create sample services with forms
flask create-sample-services

# Create demo data (sample requests, queries)
flask create-demo-data

# Run database migrations
flask db upgrade

# Create new migration after model changes
flask db migrate -m "Description of changes"
```

---

## Running Tests

### Setup Test Environment

```bash
cd backend

# Install test dependencies
pip install -r requirements-test.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestLogin

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Test Summary

| Module | Tests | Coverage |
|--------|-------|----------|
| Authentication | 21 tests | Login, OTP, Password Reset |
| Users | 18 tests | Profile, Invite, List, Toggle |
| Companies | 12 tests | CRUD, Plans, Multi-tenant |
| Services | 20 tests | Catalog, Requests, Workflow |
| Forms | 12 tests | CRUD, Responses, Validation |
| Documents | 10 tests | Upload, Download, Access |
| Notifications | 15 tests | Email, Templates, Automation |
| Analytics | 8 tests | Dashboard, Revenue, Workload |

---

## Project Structure

```
Jaypee_crm/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory + CLI commands
│   │   ├── config.py                # Configuration classes
│   │   ├── extensions.py            # Flask extensions
│   │   ├── common/                  # Shared utilities
│   │   │   ├── decorators.py        # Auth decorators
│   │   │   ├── responses.py         # API response helpers
│   │   │   └── export.py            # CSV/Excel export
│   │   └── modules/
│   │       ├── user/                # Authentication & Users
│   │       ├── company/             # Company Management
│   │       ├── services/            # Service Requests
│   │       ├── forms/               # Dynamic Forms
│   │       ├── documents/           # File Storage
│   │       ├── notifications/       # Email & Notifications
│   │       ├── payments/            # Stripe Integration
│   │       ├── analytics/           # Dashboard & Reports
│   │       ├── tags/                # User Tagging
│   │       ├── search/              # Global Search
│   │       └── audit/               # Activity Logging
│   ├── tests/                       # Pytest test suite
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-test.txt        # Test dependencies
│   └── run.py                       # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Route pages
│   │   ├── services/api.js          # API client
│   │   └── store/                   # Zustand state
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml               # Docker orchestration
├── .env.example                     # Environment template
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask (Python 3.10+) |
| **Frontend** | React 18 + Vite + TailwindCSS |
| **Database** | PostgreSQL 14+ |
| **Authentication** | JWT + Email OTP |
| **Payments** | Stripe |
| **File Storage** | Azure Blob / Local |
| **Email** | Microsoft Graph API |
| **Testing** | Pytest + pytest-flask |
| **Containerization** | Docker + Docker Compose |

---

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Login (sends OTP if 2FA enabled) |
| POST | `/verify-otp` | Verify OTP and get tokens |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with OTP |
| GET | `/me` | Get current user info |
| POST | `/refresh` | Refresh access token |

### Users (`/api/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/invite` | Invite new user (Admin) |
| GET | `/` | List users (Admin) |
| GET | `/:id` | Get user details |
| PATCH | `/profile` | Update own profile |
| POST | `/change-password` | Change password |
| POST | `/:id/toggle-status` | Activate/deactivate user |
| GET | `/accountants` | List accountants for assignment |

### Companies (`/api/companies`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create company (Super Admin) |
| GET | `/` | List all companies (Super Admin) |
| GET | `/:id` | Get company details |
| PATCH | `/:id` | Update company |
| GET | `/my-company` | Get own company |
| GET | `/plans` | Get available plans |

### Services (`/api/services`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List services |
| POST | `/` | Create service (Admin) |
| PATCH | `/:id` | Update service (Admin) |
| GET | `/defaults` | List default services |
| POST | `/defaults/:id/activate` | Activate service for company |

### Service Requests (`/api/requests`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List requests (role-filtered) |
| POST | `/` | Create request(s) |
| GET | `/:id` | Get request details |
| POST | `/:id/assign` | Assign to accountant (Admin) |
| PATCH | `/:id/status` | Update status |
| PATCH | `/:id/invoice` | Update invoice details |
| POST | `/:id/notes` | Add internal note |
| GET | `/:id/queries` | Get queries |
| POST | `/:id/queries` | Post query/message |

### Payments (`/api/payments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/config` | Get Stripe public key |
| POST | `/invoices/:id/checkout` | Create checkout session |
| POST | `/invoices/:id/payment-link` | Generate payment link |
| POST | `/webhook` | Stripe webhook handler |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List notifications |
| GET | `/unread-count` | Get unread count |
| PATCH | `/:id/read` | Mark as read |
| GET | `/email-templates` | List email templates |
| POST | `/email-templates` | Create template |
| GET | `/automations` | List automations |
| POST | `/automations` | Create automation |

---

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/accountant_crm

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Stripe (Optional - for payments)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Azure Blob Storage (Optional - for documents)
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER=crm-documents

# Microsoft Graph API (Optional - for email)
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret
GRAPH_TENANT_ID=your-tenant-id
GRAPH_SENDER_EMAIL=noreply@yourcompany.com
```

---

## User Roles & Permissions

| Role | Scope | Can Create Users | Can Assign | Can Raise Invoice |
|------|-------|------------------|------------|-------------------|
| **Super Admin** | All Companies | ✅ Any role | ✅ | ✅ |
| **Admin** | Own Company | ✅ Accountant/User | ✅ | ✅ |
| **Accountant** | Assigned Only | ❌ | ❌ | ❌ |
| **User (Client)** | Own Only | ❌ | ❌ | ❌ |

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see LICENSE file for details.

---

## Support

For issues and questions, please create an issue on GitHub:
https://github.com/Adarsh-Aggarwal98/Jaypee_crm/issues
