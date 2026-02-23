# ClientEntity Feature Documentation

## Overview

This document describes the ClientEntity feature implementation for handling:
1. **External Accountants** managing multiple client organizations
2. **POC (Point of Contact) changes** while preserving organizational history

---

## Business Problem

### Scenario 1: External Accountant
An external accountant (CPA firm) manages services for multiple client organizations:
- ABC Pty Ltd (company)
- Smith Family Trust (trust)
- John's SMSF (self-managed super fund)

**Current Problem:** When the accountant creates a service request, it's tied to their user account, not the client organization. Form fields capture accountant's info instead of client's.

### Scenario 2: POC Change
A company comes for audit services with John as the point of contact:
- John creates account, submits requests
- John leaves the company
- Mary takes over as new POC

**Current Problem:** All historical records are tied to John's user account. When John is deactivated, the company loses access to its history.

---

## Solution: ClientEntity Model

### Architecture

```
Company (Accounting Practice)
    │
    ├── Users (Staff: Admins, Accountants)
    │
    └── ClientEntity (Client Organizations)
            │
            ├── entity_type: COMPANY/TRUST/SMSF/PARTNERSHIP/INDIVIDUAL
            ├── name, trading_name, abn, acn, tfn
            ├── trust_type, trustee_name, trust_deed_date (for trusts)
            │
            ├── ClientEntityContact[] (POCs with history)
            │       ├── first_name, last_name, email, phone
            │       ├── position (Director, Trustee, etc.)
            │       ├── user_id (optional - if has login)
            │       ├── effective_from / effective_to (temporal tracking)
            │       └── is_primary, is_active
            │
            └── ServiceRequest[] (work for this entity)
                    ├── client_entity_id (links to organization)
                    └── user_id (who submitted the request)
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **ClientEntity** | Represents a client organization (company, trust, SMSF, etc.) |
| **ClientEntityContact** | A person associated with an entity, with effective dates for history |
| **Entity Types** | COMPANY, TRUST, SMSF, PARTNERSHIP, INDIVIDUAL, SOLE_TRADER, OTHER |
| **Trust Types** | discretionary, unit, hybrid, fixed |

---

## Database Schema

### Table: `client_entities`

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) | Primary key (UUID) |
| company_id | VARCHAR(36) | FK to companies (which practice manages this) |
| name | VARCHAR(200) | Legal name |
| trading_name | VARCHAR(200) | Trading/business name |
| entity_type | VARCHAR(50) | COMPANY, TRUST, SMSF, etc. |
| abn | VARCHAR(20) | Australian Business Number |
| acn | VARCHAR(20) | Australian Company Number |
| tfn | VARCHAR(20) | Tax File Number |
| trust_type | VARCHAR(50) | For trusts: discretionary, unit, hybrid, fixed |
| trustee_name | VARCHAR(200) | For trusts: name of trustee |
| trust_deed_date | DATE | For trusts: date of trust deed |
| email | VARCHAR(120) | Entity contact email |
| phone | VARCHAR(20) | Entity contact phone |
| address_line1 | VARCHAR(200) | Address |
| address_line2 | VARCHAR(200) | Address line 2 |
| city | VARCHAR(100) | City |
| state | VARCHAR(50) | State |
| postcode | VARCHAR(10) | Postcode |
| country | VARCHAR(100) | Country (default: Australia) |
| financial_year_end_month | INTEGER | FY end month (default: 6 for June) |
| financial_year_end_day | INTEGER | FY end day (default: 30) |
| xero_contact_id | VARCHAR(100) | External integration ID |
| is_active | BOOLEAN | Active status |
| notes | TEXT | Notes |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| created_by_id | VARCHAR(36) | FK to users |

### Table: `client_entity_contacts`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| client_entity_id | VARCHAR(36) | FK to client_entities |
| user_id | VARCHAR(36) | FK to users (optional - if has login) |
| first_name | VARCHAR(100) | Contact first name |
| last_name | VARCHAR(100) | Contact last name |
| email | VARCHAR(120) | Contact email |
| phone | VARCHAR(20) | Contact phone |
| position | VARCHAR(100) | Position (Director, Trustee, etc.) |
| contact_type | VARCHAR(20) | PRIMARY, BILLING, TECHNICAL, COMPLIANCE, OTHER |
| is_primary | BOOLEAN | Is primary contact |
| effective_from | DATE | When contact became active |
| effective_to | DATE | When contact ended (NULL = still active) |
| is_active | BOOLEAN | Active status |
| notes | TEXT | Notes |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Modified Table: `service_requests`

| New Column | Type | Description |
|------------|------|-------------|
| client_entity_id | VARCHAR(36) | FK to client_entities (nullable) |

---

## API Endpoints

### ClientEntity CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/client-entities` | List entities for company |
| POST | `/client-entities` | Create new entity |
| GET | `/client-entities/<id>` | Get entity details |
| PATCH | `/client-entities/<id>` | Update entity |
| DELETE | `/client-entities/<id>` | Soft delete entity |
| GET | `/client-entities/search?q=` | Search by name/ABN |

### ClientEntityContact CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/client-entities/<id>/contacts` | List contacts |
| POST | `/client-entities/<id>/contacts` | Add contact |
| PATCH | `/client-entities/<id>/contacts/<cid>` | Update contact |

### Modified Endpoints

| Method | Endpoint | Change |
|--------|----------|--------|
| POST | `/requests` | Accept optional `client_entity_id` |
| GET | `/requests/<id>` | Include `client_entity` in response |

---

## Frontend Integration

### NewServiceRequest.jsx Changes

For admins/external accountants, add optional entity selection step:

```
Step 0: Select Client Entity (optional)
    ↓
Step 1: Select Client User (existing)
    ↓
Step 2: Select Services
    ↓
Step 3: Fill Details
    ↓
Step 4: Review & Submit
```

### New Components

| Component | Purpose |
|-----------|---------|
| `ClientEntitySelector` | Dropdown/search for selecting entity |
| `ClientEntityForm` | Create/edit entity form |
| `ClientEntityCard` | Display card for entity |
| `ClientEntityContactList` | List contacts with history |

### New Pages

| Page | Purpose |
|------|---------|
| `ClientEntityList` | Admin list of all entities |
| `ClientEntityDetail` | Entity detail with contacts and requests |

---

## Data Migration

### Auto-Migration Strategy

The migration will automatically create ClientEntities from existing users' `company_name` field:

1. **Create entities** from distinct `(company_id, company_name)` pairs
2. **Create contacts** linking users to their entities
3. **Link requests** to entities via user's company_name

This ensures backwards compatibility while enabling the new functionality.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Entity selection | Optional | Allows gradual adoption |
| Trust fields | Included | trust_type, trustee_name, trust_deed_date |
| Data migration | Auto-migrate | Create from existing company_name |
| client_entity_id | Nullable | Backwards compatible |

---

## Files Structure

### Backend

```
backend/app/modules/client_entity/
├── __init__.py          # Blueprint registration
├── models.py            # ClientEntity, ClientEntityContact
├── schemas.py           # Marshmallow validation
├── repositories.py      # Data access layer
├── usecases.py          # Business logic
└── routes.py            # API endpoints
```

### Migrations

```
backend/sql_migrations/
├── upgrade_db_1.sql     # Schema changes
└── data_migration_1.py  # Auto-migration logic
```

### Frontend

```
frontend/src/
├── components/features/client-entities/
│   ├── ClientEntitySelector.jsx
│   ├── ClientEntityForm.jsx
│   └── ClientEntityCard.jsx
├── pages/client-entities/
│   ├── ClientEntityList.jsx
│   └── ClientEntityDetail.jsx
└── services/api.js      # Add clientEntitiesAPI
```

---

## Usage Examples

### Creating Request with Entity (API)

```javascript
// POST /requests
{
  "service_ids": [1, 2, 3],
  "user_id": "user-uuid",           // Optional: on behalf of
  "client_entity_id": "entity-uuid", // Optional: for which entity
  "description": "Annual audit"
}
```

### Response with Entity

```javascript
// GET /requests/<id>
{
  "id": "request-uuid",
  "request_number": "REQ-000123",
  "user": { "id": "...", "full_name": "John Smith" },
  "client_entity": {
    "id": "entity-uuid",
    "name": "ABC Pty Ltd",
    "entity_type": "COMPANY",
    "abn": "12345678901"
  },
  "service": { ... },
  "status": "pending"
}
```

### POC Change Flow

```sql
-- John leaves, Mary takes over

-- 1. End John's contact
UPDATE client_entity_contacts
SET effective_to = '2024-06-30', is_active = FALSE
WHERE client_entity_id = 'entity-uuid' AND user_id = 'john-uuid';

-- 2. Add Mary as new contact
INSERT INTO client_entity_contacts (
  client_entity_id, user_id, first_name, last_name,
  email, is_primary, effective_from
) VALUES (
  'entity-uuid', 'mary-uuid', 'Mary', 'Jones',
  'mary@abc.com', TRUE, '2024-07-01'
);
```

---

## Testing

### Verification Commands

```bash
# Check tables created
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c '\dt client*'"

# Check entities created
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c 'SELECT COUNT(*) FROM client_entities;'"

# Check linked requests
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c 'SELECT COUNT(*) FROM service_requests WHERE client_entity_id IS NOT NULL;'"
```

### Rollback

```sql
ALTER TABLE service_requests DROP COLUMN IF EXISTS client_entity_id;
DROP TABLE IF EXISTS client_entity_contacts;
DROP TABLE IF EXISTS client_entities;
UPDATE db_version SET version = 0;
```

---

## Related Files

| File | Purpose |
|------|---------|
| `docs/CLIENT_ENTITY_TRACKER.md` | Implementation progress tracker |
| `backend/sql_migrations/upgrade_db_1.sql` | SQL migration |
| `backend/sql_migrations/data_migration_1.py` | Python migration |
| `backend/app/modules/services/models.py` | ServiceRequest model (modified) |

---

*Last Updated: 2026-01-31*
