# ClientEntity Feature - Implementation Tracker

## Status: 🟡 In Progress

**Start Date:** 2026-01-31
**Target Completion:** TBD
**Last Updated:** 2026-01-31

---

## Quick Links

| Document | Path |
|----------|------|
| Feature Documentation | `docs/CLIENT_ENTITY_FEATURE.md` |
| SQL Migration | `backend/sql_migrations/upgrade_db_1.sql` |
| Python Migration | `backend/sql_migrations/data_migration_1.py` |
| Backend Module | `backend/app/modules/client_entity/` |

---

## Implementation Phases

### Phase 1: Database & Backend Core

| Task | Status | File(s) | Notes |
|------|--------|---------|-------|
| Create upgrade_db_1.sql | ✅ Done | `backend/sql_migrations/upgrade_db_1.sql` | Tables + indexes |
| Create data_migration_1.py | ✅ Done | `backend/sql_migrations/data_migration_1.py` | Auto-migrate from company_name |
| Update create_db.sql | ✅ Done | `backend/sql_migrations/create_db.sql` | Add new tables |
| Create models.py | ✅ Done | `backend/app/modules/client_entity/models.py` | ClientEntity, ClientEntityContact |
| Create schemas.py | ✅ Done | `backend/app/modules/client_entity/schemas.py` | Validation schemas |
| Create repositories.py | ✅ Done | `backend/app/modules/client_entity/repositories.py` | Data access |
| Create usecases.py | ✅ Done | `backend/app/modules/client_entity/usecases.py` | Business logic |
| Create routes.py | ✅ Done | `backend/app/modules/client_entity/routes.py` | API endpoints |
| Create __init__.py | ✅ Done | `backend/app/modules/client_entity/__init__.py` | Blueprint |
| Register blueprint | ✅ Done | `backend/app/__init__.py` | Import & register |

### Phase 2: ServiceRequest Integration

| Task | Status | File(s) | Notes |
|------|--------|---------|-------|
| Add client_entity_id to model | ✅ Done | `backend/app/modules/services/models.py` | New FK column |
| Update CreateRequestSchema | ✅ Done | `backend/app/modules/services/schemas.py` | Accept entity ID |
| Modify create_request route | ✅ Done | `backend/app/modules/services/routes.py` | Handle entity |
| Update to_dict() output | ✅ Done | `backend/app/modules/services/models.py` | Include entity |
| Update usecases | ✅ Done | `backend/app/modules/services/usecases.py` | Pass entity to ServiceRequest |

### Phase 3: Frontend - Entity Management

| Task | Status | File(s) | Notes |
|------|--------|---------|-------|
| Add clientEntitiesAPI | ✅ Done | `frontend/src/services/api.js` | API methods |
| Create ClientEntitySelector | ✅ Done | `frontend/src/components/features/client-entities/ClientEntitySelector.jsx` | Searchable dropdown |
| Create ClientEntityForm | ✅ Done | `frontend/src/components/features/client-entities/ClientEntityForm.jsx` | Create/edit form |
| Create ClientEntityList page | ✅ Done | `frontend/src/pages/client-entities/ClientEntityList.jsx` | Admin list |
| Create ClientEntityDetail page | ✅ Done | `frontend/src/pages/client-entities/ClientEntityDetail.jsx` | Detail view |
| Add routes | ✅ Done | `frontend/src/App.jsx` | /client-entities routes |
| Add sidebar nav | ✅ Done | `frontend/src/components/layout/Sidebar.jsx` | Navigation link |

### Phase 4: Frontend - Request Flow

| Task | Status | File(s) | Notes |
|------|--------|---------|-------|
| Modify NewServiceRequest.jsx | ✅ Done | `frontend/src/pages/services/NewServiceRequest.jsx` | Added entity selector |
| Update requestsAPI.create | ✅ Done | `frontend/src/services/api.js` | Pass entity ID |
| Show entity in request details | ✅ Done | `frontend/src/pages/requests/RequestDetail.jsx` | Display entity info |

### Phase 5: Testing & Deployment

| Task | Status | Notes |
|------|--------|-------|
| Test migration locally | ⬜ Pending | Docker compose |
| Backup production DB | ⬜ Pending | Before deploying |
| Deploy to remote VM | ⬜ Pending | Run migration |
| Verify data migration | ⬜ Pending | Check counts |
| Test entity CRUD | ⬜ Pending | API testing |
| Test request flow | ⬜ Pending | End-to-end |

---

## Database State

### Remote VM (accountant_crm)

| Table | Count | Last Checked |
|-------|-------|--------------|
| users | 146 | 2026-01-31 |
| companies | 3 | 2026-01-31 |
| services | 73 | 2026-01-31 |
| service_requests | 97 | 2026-01-31 |
| client_entities | - | Not created yet |
| client_entity_contacts | - | Not created yet |

### Expected After Migration

| Metric | Expected |
|--------|----------|
| client_entities created | ~TBD (depends on unique company_name values) |
| client_entity_contacts created | ~TBD (one per user with company_name) |
| service_requests linked | ~TBD (requests where user has company_name) |

---

## Key Design Decisions

| Decision | Choice | Date |
|----------|--------|------|
| Entity selection required? | Optional for everyone | 2026-01-31 |
| Include trust-specific fields? | Yes (trust_type, trustee_name, trust_deed_date) | 2026-01-31 |
| Auto-migrate existing data? | Yes, from users.company_name | 2026-01-31 |

---

## Files Modified/Created

### Created Files

| File | Status | Description |
|------|--------|-------------|
| `docs/CLIENT_ENTITY_FEATURE.md` | ✅ Created | Feature documentation |
| `docs/CLIENT_ENTITY_TRACKER.md` | ✅ Created | This tracker |
| `backend/sql_migrations/upgrade_db_1.sql` | ⬜ Pending | SQL migration |
| `backend/sql_migrations/data_migration_1.py` | ⬜ Pending | Python migration |
| `backend/app/modules/client_entity/__init__.py` | ⬜ Pending | Module init |
| `backend/app/modules/client_entity/models.py` | ⬜ Pending | Models |
| `backend/app/modules/client_entity/schemas.py` | ⬜ Pending | Schemas |
| `backend/app/modules/client_entity/repositories.py` | ⬜ Pending | Repositories |
| `backend/app/modules/client_entity/usecases.py` | ⬜ Pending | Use cases |
| `backend/app/modules/client_entity/routes.py` | ⬜ Pending | Routes |

### Modified Files

| File | Status | Changes |
|------|--------|---------|
| `backend/sql_migrations/create_db.sql` | ⬜ Pending | Add new tables |
| `backend/app/__init__.py` | ⬜ Pending | Register blueprint |
| `backend/app/modules/services/models.py` | ⬜ Pending | Add client_entity_id |
| `backend/app/modules/services/schemas.py` | ⬜ Pending | Update schema |
| `backend/app/modules/services/routes.py` | ⬜ Pending | Handle entity |
| `frontend/src/services/api.js` | ⬜ Pending | Add API methods |
| `frontend/src/pages/services/NewServiceRequest.jsx` | ⬜ Pending | Add entity step |

---

## Commands Reference

### Check Remote DB
```bash
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c 'SELECT version FROM db_version;'"
```

### Run Migration
```bash
python remote_deploy.py "docker exec jaypee-crm-backend python sql_migrations/migration_runner.py"
```

### Verify Tables
```bash
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c '\dt client*'"
```

### Count Entities
```bash
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c 'SELECT COUNT(*) FROM client_entities;'"
```

### Rollback
```bash
python remote_deploy.py "docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c \"ALTER TABLE service_requests DROP COLUMN IF EXISTS client_entity_id; DROP TABLE IF EXISTS client_entity_contacts; DROP TABLE IF EXISTS client_entities; UPDATE db_version SET version = 0;\""
```

---

## Issues & Blockers

| Issue | Status | Resolution |
|-------|--------|------------|
| None yet | - | - |

---

## Notes

### 2026-01-31 (Session 2)
- Completed Phase 2: ServiceRequest Integration
  - Updated CreateRequestSchema to accept client_entity_id
  - Modified create_request route to pass client_entity_id
  - Updated usecases.py to validate and use client_entity_id
- Completed Phase 3: Frontend - Entity Management
  - Added clientEntitiesAPI to api.js
  - Created ClientEntitySelector and ClientEntityForm components
  - Created ClientEntityList and ClientEntityDetail pages
  - Added routes and sidebar navigation
- Completed Phase 4: Frontend - Request Flow
  - Modified NewServiceRequest.jsx with entity selector for admins
  - Updated requestsAPI.create to pass entity ID
  - Added entity display in RequestDetail.jsx
- All backend and frontend code complete, ready for Phase 5 (Testing & Deployment)

### 2026-01-31
- Created feature documentation
- Created implementation tracker
- Approved design decisions with user
- Completed Phase 1: Database & Backend Core

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Pending |
| 🔄 | In Progress |
| ✅ | Completed |
| ❌ | Blocked |
| ⏸️ | On Hold |

---

*This document should be updated as implementation progresses.*
