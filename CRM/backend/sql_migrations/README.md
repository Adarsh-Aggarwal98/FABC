# Database Migration System

## Overview

This migration system manages database schema changes and data migrations for the CRM application. It ensures that database changes are versioned, tracked, and applied consistently across all environments (development, staging, production).

---

## Table of Contents

1. [File Structure](#file-structure)
2. [How It Works](#how-it-works)
3. [Version Tracking](#version-tracking)
4. [Writing Migrations](#writing-migrations)
5. [Running Migrations](#running-migrations)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Examples](#examples)

---

## File Structure

```
backend/sql_migrations/
├── README.md                    # This documentation
├── migration_runner.py          # Migration execution script
├── create_db.sql                # Complete schema (fresh installs)
├── seed_data.sql                # Optional seed data (for fresh installs)
├── upgrade_db_1.sql             # Migration version 1
├── upgrade_db_2.sql             # Migration version 2
├── data_migration_1.py          # Python migration version 1 (optional)
└── ...
```

### File Descriptions

| File | Purpose |
|------|---------|
| `migration_runner.py` | Core script that detects and runs pending migrations |
| `create_db.sql` | Complete database schema for fresh installations |
| `seed_data.sql` | Seed data to populate fresh database (optional) |
| `upgrade_db_X.sql` | SQL migration for version X (schema + data changes) |
| `data_migration_X.py` | Python migration for version X (complex logic only) |

---

## How It Works

### Automatic Execution Flow

```
Docker Container Starts
        ↓
entrypoint.sh runs
        ↓
Waits for database to be ready
        ↓
Runs flask init-db (creates roles, default data)
        ↓
Runs sql_migrations/migration_runner.py
        ↓
Runs flask create-sample-services
        ↓
Starts Flask server
```

### Migration Runner Logic

```python
1. Connect to database
2. Check/create db_version table
3. Get current version from db_version table
4. Scan for upgrade_db_*.sql and data_migration_*.py files
5. Filter migrations where version > current_version
6. Sort by version number (SQL runs before Python for same version)
7. Execute each pending migration
8. Update db_version to highest successful version
9. Report results
```

---

## Version Tracking

### Database Table

The system uses a `db_version` table to track the current schema version:

```sql
CREATE TABLE db_version (
    id INTEGER PRIMARY KEY DEFAULT 1,
    version INTEGER NOT NULL DEFAULT 0,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT single_row CHECK (id = 1)
);
```

### Version Rules

- Version numbers are **integers** (1, 2, 3, ... 100, 101, ...)
- Versions must be **sequential** but can have gaps
- If current version is 5, migrations 6, 7, 8... will run
- Both SQL and Python migrations with same version run together (SQL first)

### Example Scenario

```
Current DB Version: 5

Available migrations:
- upgrade_db_3.sql    (skipped - already applied)
- upgrade_db_5.sql    (skipped - already applied)
- upgrade_db_6.sql    (WILL RUN)
- upgrade_db_7.sql    (WILL RUN)
- data_migration_7.py (WILL RUN - after upgrade_db_7.sql)
- upgrade_db_10.sql   (WILL RUN)

Result: Runs 6, 7, 7(py), 10 → New version: 10
```

---

## Writing Migrations

### Step 1: Determine Next Version

```bash
# Check current version in database
docker exec crm-db-local psql -U postgres -d accountant_crm -c "SELECT version FROM db_version;"

# Or check existing migration files
ls backend/sql_migrations/upgrade_db_*.sql
```

If the highest existing migration is `upgrade_db_5.sql`, create `upgrade_db_6.sql`.

### Step 2: Create SQL Migration File

**Filename format:** `upgrade_db_X.sql` where X is the version number.

```sql
-- upgrade_db_6.sql
-- ============================================================================
-- UPGRADE_DB_6.SQL - Add User Preferences
-- ============================================================================
-- Author: Your Name
-- Date: 2026-01-25
-- Description: Adds user preferences table and notification settings
-- ============================================================================

-- Add new table
CREATE TABLE IF NOT EXISTS user_preferences (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Add column to existing table
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences_id VARCHAR(36);

-- Create index
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id);

-- Insert default data
INSERT INTO user_preferences (user_id, email_notifications)
SELECT id, TRUE FROM users WHERE id NOT IN (SELECT user_id FROM user_preferences)
ON CONFLICT DO NOTHING;

-- Update existing data
UPDATE users SET is_active = TRUE WHERE is_active IS NULL;
```

### Step 3: Update create_db.sql

**Important:** Always add the same changes to `create_db.sql` for fresh installations.

```sql
-- In create_db.sql, add the new table definition
CREATE TABLE IF NOT EXISTS user_preferences (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

### Step 4: Create Python Migration (Optional)

Only create Python migrations when you need:
- Complex conditional logic
- Loops over data
- External API calls
- Data transformations that are difficult in SQL

**Filename format:** `data_migration_X.py` where X is the version number.

```python
# data_migration_6.py
"""
Data Migration 6: Populate User Preferences
===========================================
Creates default preferences for all existing users based on their role.
"""

def migrate(conn, cursor):
    """
    Migration function called by migration_runner.py

    Args:
        conn: psycopg2 connection object
        cursor: psycopg2 cursor (RealDictCursor)
    """
    print("    Fetching users without preferences...")

    cursor.execute("""
        SELECT u.id, u.email, r.name as role_name
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.id NOT IN (SELECT user_id FROM user_preferences)
    """)
    users = cursor.fetchall()

    print(f"    Found {len(users)} users to process...")

    for user in users:
        # Complex logic: admins get all notifications, users get email only
        email_notif = True
        sms_notif = user['role_name'] in ('admin', 'super_admin')
        theme = 'dark' if user['role_name'] == 'super_admin' else 'light'

        cursor.execute("""
            INSERT INTO user_preferences (user_id, email_notifications, sms_notifications, theme)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user['id'], email_notif, sms_notif, theme))

    conn.commit()
    print(f"    Created preferences for {len(users)} users")
```

---

## Running Migrations

### Automatic (Recommended)

Migrations run automatically when the Docker container starts:

```bash
# Start/restart containers - migrations run automatically
docker-compose -f docker-compose.local.yml up -d

# Or restart just the backend
docker-compose -f docker-compose.local.yml restart backend
```

### Manual Execution

```bash
# Run from inside the container
docker exec crm-backend-local python sql_migrations/migration_runner.py

# Or with shell
docker exec -it crm-backend-local sh -c "python sql_migrations/migration_runner.py"
```

### Check Current Version

```bash
# Check database version
docker exec crm-db-local psql -U postgres -d accountant_crm -c "SELECT * FROM db_version;"

# List applied migrations (if using schema_migrations table)
docker exec crm-db-local psql -U postgres -d accountant_crm -c "SELECT * FROM schema_migrations ORDER BY version;"
```

### Run Specific SQL File Manually

```bash
# Run a specific SQL file (use with caution)
cat backend/sql_migrations/upgrade_db_6.sql | docker exec -i crm-db-local psql -U postgres -d accountant_crm
```

---

## Best Practices

### DO ✅

1. **Always use IF NOT EXISTS / IF EXISTS**
   ```sql
   CREATE TABLE IF NOT EXISTS users (...);
   ALTER TABLE users ADD COLUMN IF NOT EXISTS new_column VARCHAR(100);
   DROP TABLE IF EXISTS old_table;
   ```

2. **Use ON CONFLICT for inserts**
   ```sql
   INSERT INTO settings (key, value) VALUES ('theme', 'dark')
   ON CONFLICT (key) DO NOTHING;

   -- Or update on conflict
   ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
   ```

3. **Make migrations idempotent** (safe to run multiple times)

4. **Add indexes for new foreign keys**
   ```sql
   ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_id VARCHAR(36);
   CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
   ```

5. **Test migrations on a copy of production data**

6. **Keep migrations small and focused**

7. **Document complex migrations with comments**

### DON'T ❌

1. **Don't modify or delete old migration files** - Create new ones instead

2. **Don't use DROP COLUMN without backup** - Data will be lost

3. **Don't skip version numbers unnecessarily** - Keep them sequential

4. **Don't put destructive operations without WHERE clause**
   ```sql
   -- DANGEROUS: Deletes all rows!
   DELETE FROM users;

   -- SAFE: Deletes specific rows
   DELETE FROM users WHERE is_deleted = TRUE AND deleted_at < NOW() - INTERVAL '30 days';
   ```

5. **Don't forget to update create_db.sql**

---

## Troubleshooting

### Migration Failed - How to Retry

```bash
# 1. Check the error in logs
docker logs crm-backend-local 2>&1 | grep -A 20 "MIGRATION"

# 2. Fix the SQL file

# 3. If needed, manually set version back
docker exec crm-db-local psql -U postgres -d accountant_crm -c "UPDATE db_version SET version = 5;"

# 4. Restart to retry
docker-compose -f docker-compose.local.yml restart backend
```

### Check What Columns Exist

```bash
# Describe a table
docker exec crm-db-local psql -U postgres -d accountant_crm -c "\d users"

# Check if column exists
docker exec crm-db-local psql -U postgres -d accountant_crm -c "
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'phone_verified';
"
```

### Reset Database (Development Only)

```bash
# WARNING: Destroys all data!
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up -d
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `column already exists` | Migration ran partially | Use `ADD COLUMN IF NOT EXISTS` |
| `relation does not exist` | Table not created yet | Check migration order |
| `duplicate key value` | Insert conflict | Use `ON CONFLICT DO NOTHING` |
| `permission denied` | Wrong user | Check DB_USER environment variable |

---

## Examples

### Example 1: Add New Column

```sql
-- upgrade_db_7.sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code VARCHAR(10);
CREATE INDEX IF NOT EXISTS idx_users_phone_verified ON users(phone_verified);
```

### Example 2: Add New Table with Foreign Key

```sql
-- upgrade_db_8.sql
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
```

### Example 3: Data Migration with Business Logic

```sql
-- upgrade_db_9.sql
-- Migrate status values to new format
UPDATE service_requests
SET status = 'in_progress'
WHERE status IN ('processing', 'working', 'active');

UPDATE service_requests
SET status = 'pending_review'
WHERE status = 'review';
```

### Example 4: Complex Python Migration

```python
# data_migration_10.py
"""
Recalculate all invoice totals based on new tax rules.
"""
from decimal import Decimal

def migrate(conn, cursor):
    cursor.execute("SELECT id, subtotal, tax_rate FROM invoices WHERE total IS NULL")
    invoices = cursor.fetchall()

    for inv in invoices:
        subtotal = Decimal(str(inv['subtotal'] or 0))
        tax_rate = Decimal(str(inv['tax_rate'] or 10)) / 100
        total = subtotal * (1 + tax_rate)

        cursor.execute(
            "UPDATE invoices SET total = %s WHERE id = %s",
            (float(total), inv['id'])
        )

    conn.commit()
    print(f"    Updated {len(invoices)} invoice totals")
```

---

## Quick Reference

### Create New Migration Checklist

- [ ] Determine next version number
- [ ] Create `upgrade_db_X.sql` with changes
- [ ] Use `IF NOT EXISTS` / `ON CONFLICT` for safety
- [ ] Update `create_db.sql` with same changes
- [ ] Create `data_migration_X.py` if complex logic needed
- [ ] Test locally
- [ ] Commit and deploy

### Commands Cheat Sheet

```bash
# Check current version
docker exec crm-db-local psql -U postgres -d accountant_crm -c "SELECT version FROM db_version;"

# Run migrations manually
docker exec crm-backend-local python sql_migrations/migration_runner.py

# View table structure
docker exec crm-db-local psql -U postgres -d accountant_crm -c "\d tablename"

# View migration logs
docker logs crm-backend-local 2>&1 | grep -A 30 "MIGRATION"

# Set version manually (use with caution)
docker exec crm-db-local psql -U postgres -d accountant_crm -c "UPDATE db_version SET version = X;"
```

---

## Who Runs Migrations?

| Environment | Trigger | Who/What Runs It |
|-------------|---------|------------------|
| Local Docker | Container start | `entrypoint.sh` → `migration_runner.py` |
| Development | Container restart | Automatic via entrypoint |
| Staging | Deployment | CI/CD pipeline or manual |
| Production | Deployment | CI/CD pipeline with approval |

---

## Support

For issues with migrations:
1. Check container logs: `docker logs crm-backend-local`
2. Check database state: `\d tablename` in psql
3. Review migration file for errors
4. Test migration on development database first

---

## Production Commands

### IMPORTANT: UTF-8 Encoding

PostgreSQL requires UTF-8 encoded SQL files. Always follow these rules:

1. **Run commands directly on the Linux server** (SSH into server first)
2. **Never copy/paste SQL content through Windows editors** (they convert to UTF-16)
3. **Never open SQL files in Windows Notepad** (saves as UTF-16)
4. **Use `file` command to verify encoding** before committing

```bash
# Check file encoding (should show "UTF-8" or "ASCII")
file backend/sql_migrations/create_db.sql
file backend/sql_migrations/seed_data.sql

# If file shows "UTF-16", convert it:
iconv -f UTF-16LE -t UTF-8 filename.sql > filename_utf8.sql
mv filename_utf8.sql filename.sql

# Remove BOM if present (shows "with BOM" in file output)
sed -i '1s/^\xEF\xBB\xBF//' filename.sql
```

---

### Generate New create_db.sql from Existing Database

When your database has evolved and you need to regenerate `create_db.sql`:

```bash
# SSH into production server
ssh root@your-server

# Export schema only (no data) - UTF-8 encoding guaranteed
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --schema-only \
    --no-owner \
    --no-privileges \
    --encoding=UTF8 \
    > /root/Jaypee_crm/backend/sql_migrations/create_db.sql

# Verify encoding
file /root/Jaypee_crm/backend/sql_migrations/create_db.sql
```

### Generate seed_data.sql from Existing Database

```bash
# SSH into production server
ssh root@your-server

# Export data only - UTF-8 encoding guaranteed
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --data-only \
    --encoding=UTF8 \
    > /root/Jaypee_crm/backend/sql_migrations/seed_data.sql

# Verify encoding
file /root/Jaypee_crm/backend/sql_migrations/seed_data.sql
```

### Backup & Restore Commands

#### Full Backup (Schema + Data)
```bash
# Create timestamped backup (UTF-8)
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --encoding=UTF8 \
    > /root/Jaypee_crm/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --encoding=UTF8 | gzip \
    > /root/Jaypee_crm/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Data Only Backup
```bash
# Export data without schema (UTF-8)
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --data-only \
    --encoding=UTF8 \
    > /root/Jaypee_crm/backups/data_only_$(date +%Y%m%d_%H%M%S).sql
```

#### Restore Full Backup
```bash
# Ensure database exists
docker exec jaypee-crm-db psql -U postgres -c "CREATE DATABASE accountant_crm;" 2>/dev/null || true

# Restore from backup
docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm \
    < /root/Jaypee_crm/backups/db_backup_YYYYMMDD_HHMMSS.sql

# Restore from compressed backup
gunzip -c /root/Jaypee_crm/backups/db_backup.sql.gz | \
    docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm
```

#### Restore Data Only (Schema Already Exists)
```bash
# First apply schema
docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm \
    < /root/Jaypee_crm/backend/sql_migrations/create_db.sql

# Then restore data
docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm \
    < /root/Jaypee_crm/backups/data_only_YYYYMMDD.sql
```

### Fresh Database Setup

```bash
# 1. Drop existing database (WARNING: deletes all data!)
docker exec jaypee-crm-db psql -U postgres -c "DROP DATABASE IF EXISTS accountant_crm;"

# 2. Create fresh database
docker exec jaypee-crm-db psql -U postgres -c "CREATE DATABASE accountant_crm;"

# 3. Apply schema
docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm \
    < /root/Jaypee_crm/backend/sql_migrations/create_db.sql

# 4. Initialize roles and default data
docker exec jaypee-crm-backend flask init-db

# 5. Run SQL migrations
docker exec jaypee-crm-backend python sql_migrations/migration_runner.py

# 6. Create sample services
docker exec jaypee-crm-backend flask create-sample-services
```

### Useful Diagnostic Commands

```bash
# Check if database exists
docker exec jaypee-crm-db psql -U postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='accountant_crm';"

# List all tables
docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "\dt"

# Check current migration version
docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c \
    "SELECT * FROM db_version;"

# Count rows in important tables
docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "
SELECT 'users' as table_name, count(*) FROM users
UNION ALL SELECT 'companies', count(*) FROM companies
UNION ALL SELECT 'services', count(*) FROM services
UNION ALL SELECT 'service_requests', count(*) FROM service_requests
UNION ALL SELECT 'roles', count(*) FROM roles;
"

# Check table structure
docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "\d users"
```

---

## Deploy Script Options

The `scripts/deploy.sh` script provides different database handling options:

### Usage

```bash
./deploy.sh [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--full-build` | Force rebuild all containers |
| `--backend-only` | Rebuild backend container only |
| `--frontend-only` | Rebuild frontend container only |
| `--rebuild-db` | Fresh database with schema + seed_data.sql (if exists) |
| `--rebuild-db-backup` | Fresh database with schema + restore backup data |

### Database Behavior

#### Normal Deployment (no db flags)
- Preserves existing database
- Only rebuilds backend/frontend containers
- Runs migrations on existing data

#### --rebuild-db (Fresh + Seed Data)
1. Backs up nothing (fresh start)
2. Removes database volume
3. Creates fresh database
4. Applies `create_db.sql` schema
5. Applies `seed_data.sql` if it exists
6. Runs `flask init-db` and migrations

#### --rebuild-db-backup (Fresh + Restore)
1. Backs up existing database
2. Removes database volume
3. Creates fresh database
4. Applies `create_db.sql` schema
5. Restores data from backup
6. Runs `flask init-db` and migrations

---

## Separating Schema and Data

### Generate Separate Files

**IMPORTANT:** Run these commands directly on the Linux server via SSH, not from Windows.

```bash
# SSH into server first
ssh root@your-server
cd /root/Jaypee_crm

# Export schema only (no data) - UTF-8 encoding
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --schema-only \
    --no-owner \
    --no-privileges \
    --encoding=UTF8 \
    > backend/sql_migrations/create_db.sql

# Export data only (no schema) - UTF-8 encoding
docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm \
    --data-only \
    --encoding=UTF8 \
    > backend/sql_migrations/seed_data.sql

# Verify both files are UTF-8
file backend/sql_migrations/create_db.sql
file backend/sql_migrations/seed_data.sql

# Commit and push from server
git add backend/sql_migrations/create_db.sql backend/sql_migrations/seed_data.sql
git commit -m "Update database schema and seed data"
git push origin main
```

### When to Use Each

| File | Use Case |
|------|----------|
| `create_db.sql` | Schema definition only, used for all fresh installs |
| `seed_data.sql` | Optional seed data for development/testing |
| Backup files | Production data restore |

### Workflow Example

```bash
# Development: Fresh database with seed data
./deploy.sh --rebuild-db

# Production: Fresh schema but restore existing data
./deploy.sh --rebuild-db-backup

# Normal update: Preserve database, update code
./deploy.sh
```
