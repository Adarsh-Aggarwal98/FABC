# Kanban Board Feature Documentation

## Overview

The Kanban Board feature provides a visual, drag-and-drop interface for tracking service requests. Users can choose between three views:

1. **List View** - Traditional table format with sorting and filtering
2. **Board View** - Kanban-style columns with draggable cards
3. **Workflow View** - Individual request workflow visualization (in RequestDetail)

Each accounting practice (company) can customize their status columns independently.

---

## Key Features

### 1. Kanban Board View

- **Visual columns** for each status
- **Drag-and-drop** to change request status
- **Color-coded** columns and cards
- **WIP limits** (Work-in-Progress) per column
- **Priority indicators** (color-coded border)
- **Overdue alerts** for missed deadlines

### 2. Customizable Status Columns

- Initialize custom statuses from system defaults
- Add new custom statuses
- Edit display name, color, description
- Set WIP limits per column
- Reorder columns
- Mark statuses as "final" (completed/cancelled)
- Reset to system defaults

### 3. View Toggle

- Seamlessly switch between List, Board, and Workflow views
- View preference saved to localStorage
- Available on the Service Requests page

---

## Database Schema

### system_request_statuses

Default statuses shared across all companies (seed data).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| status_key | VARCHAR(50) | Unique identifier (e.g., 'pending') |
| display_name | VARCHAR(100) | Display name (e.g., 'Pending') |
| description | TEXT | Optional description |
| color | VARCHAR(20) | Hex color code |
| position | INTEGER | Column order |
| is_final | BOOLEAN | True for completed/cancelled states |
| is_active | BOOLEAN | Whether status is active |
| created_at | TIMESTAMP | Creation timestamp |

### company_request_statuses

Custom statuses per company (when customized).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| company_id | VARCHAR(36) | FK to companies |
| status_key | VARCHAR(50) | Unique per company |
| display_name | VARCHAR(100) | Display name |
| description | TEXT | Optional description |
| color | VARCHAR(20) | Hex color code |
| position | INTEGER | Column order |
| wip_limit | INTEGER | Max items in this column (NULL = no limit) |
| is_final | BOOLEAN | True for completed/cancelled states |
| is_active | BOOLEAN | Whether status is active |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

---

## API Endpoints

### Status Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/statuses` | GET | Get statuses (custom or system defaults) |
| `/api/statuses` | POST | Create custom status |
| `/api/statuses/<id>` | PATCH | Update custom status |
| `/api/statuses/<id>` | DELETE | Delete custom status |
| `/api/statuses/system` | GET | Get system default statuses |
| `/api/statuses/initialize` | POST | Copy system defaults to company |
| `/api/statuses/reorder` | POST | Update column order |
| `/api/statuses/reset` | POST | Delete custom statuses, revert to defaults |
| `/api/statuses/lookup/<key>` | GET | Get status config by key |

---

## Frontend Components

### Kanban Components (`frontend/src/components/kanban/`)

| Component | Description |
|-----------|-------------|
| `KanbanBoard.jsx` | Main board container, fetches statuses, handles drop |
| `KanbanColumn.jsx` | Single status column with droppable zone |
| `KanbanCard.jsx` | Draggable request card |
| `ViewToggle.jsx` | Switch between List/Board/Workflow views |

### Pages

| Page | Path | Description |
|------|------|-------------|
| `RequestList.jsx` | `/requests` | Integrates ViewToggle and KanbanBoard |
| `StatusSettings.jsx` | `/settings/statuses` | Admin page to customize statuses |

---

## Backend Structure

### Status Module (`backend/app/modules/services/`)

| File | Description |
|------|-------------|
| `status_models.py` | SystemRequestStatus, CompanyRequestStatus models |
| `status_schemas.py` | Marshmallow validation schemas |
| `status_repository.py` | Data access layer |
| `status_usecases.py` | Business logic |
| `status_routes.py` | API endpoints |

---

## Default Statuses

The system comes with these default statuses:

| Key | Display Name | Color | Final |
|-----|--------------|-------|-------|
| pending | Pending | #F59E0B (Yellow) | No |
| in_progress | In Progress | #3B82F6 (Blue) | No |
| awaiting_info | Awaiting Info | #8B5CF6 (Purple) | No |
| on_hold | On Hold | #6B7280 (Gray) | No |
| completed | Completed | #10B981 (Green) | Yes |
| cancelled | Cancelled | #EF4444 (Red) | Yes |
| rejected | Rejected | #DC2626 (Dark Red) | Yes |

---

## Usage Guide

### For End Users (Staff)

1. Navigate to **Requests** page
2. Click **Board** view toggle to see Kanban board
3. Drag cards between columns to update status
4. Click a card to view request details

### For Admins

1. Navigate to **Board Statuses** in sidebar
2. Click **Customize Statuses** to enable customization
3. Add, edit, or delete statuses as needed
4. Set WIP limits to prevent column overload
5. Reorder columns by editing positions

---

## Technical Notes

### Backward Compatibility

- The `service_requests.status` field remains a VARCHAR
- Existing code using status strings continues to work
- Companies can adopt customization gradually

### Drag and Drop

- Uses native HTML5 Drag and Drop API
- No additional npm dependencies required
- Works across modern browsers

### View Persistence

- View preference stored in `localStorage.requestListView`
- Survives page refreshes and browser restarts

---

## Migration

### Running the Migration

```bash
# Check current DB version
docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "SELECT version FROM db_version;"

# Run migration
docker exec jaypee-crm-backend python sql_migrations/migration_runner.py

# Verify tables created
docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "\dt *status*"
```

### Rollback

```sql
DROP TABLE IF EXISTS company_request_statuses;
DROP TABLE IF EXISTS system_request_statuses;
UPDATE db_version SET version = 1;
```

---

*Document Version: 1.0*
*Last Updated: January 2026*
