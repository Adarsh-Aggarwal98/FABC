#!/usr/bin/env python3
"""
Database Migration Runner
=========================

This script handles database versioning and migrations.

STRUCTURE:
----------
1. create_db.sql      - Complete schema for fresh installs
2. upgrade_db_X.sql   - Incremental schema changes (X = version number)
3. data_migration_X.py - Data migrations (X = version number)

HOW TO ADD NEW MIGRATIONS:
==========================
1. Create upgrade_db_X.sql in sql_migrations/ (X = next version number)
   Example: If current version is 5, create upgrade_db_6.sql

2. Add the same changes to create_db.sql (for fresh installs)

3. If you need data migration, create data_migration_X.py

4. The runner will automatically detect and run pending migrations

EXAMPLE:
--------
# upgrade_db_6.sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_users_phone_verified ON users(phone_verified);

# Then add same columns to create_db.sql users table definition
"""

import os
import sys
import glob
import re
import importlib.util
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor


class MigrationRunner:
    """Handles versioned database migrations"""

    def __init__(self):
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'db'),
            'port': os.environ.get('DB_PORT', '5432'),
            'database': os.environ.get('DB_NAME', 'accountant_crm'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD', 'postgres')
        }
        self.migrations_dir = os.path.dirname(os.path.abspath(__file__))
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        self.conn = psycopg2.connect(**self.db_config)
        self.conn.autocommit = False
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def ensure_version_table(self):
        """Create version tracking table if it doesn't exist"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_version (
                id INTEGER PRIMARY KEY DEFAULT 1,
                version INTEGER NOT NULL DEFAULT 0,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT single_row CHECK (id = 1)
            )
        """)
        # Insert initial version if not exists
        self.cursor.execute("""
            INSERT INTO db_version (id, version) VALUES (1, 0)
            ON CONFLICT (id) DO NOTHING
        """)
        self.conn.commit()

    def get_current_version(self):
        """Get current database version"""
        self.cursor.execute("SELECT version FROM db_version WHERE id = 1")
        row = self.cursor.fetchone()
        return row['version'] if row else 0

    def set_version(self, version):
        """Update database version"""
        self.cursor.execute("""
            UPDATE db_version SET version = %s, applied_at = CURRENT_TIMESTAMP WHERE id = 1
        """, (version,))
        self.conn.commit()

    def get_available_migrations(self):
        """Get all available SQL migrations sorted by version"""
        pattern = os.path.join(self.migrations_dir, 'upgrade_db_*.sql')
        files = glob.glob(pattern)

        migrations = []
        for filepath in files:
            filename = os.path.basename(filepath)
            # Extract version number from filename: upgrade_db_123.sql -> 123
            match = re.match(r'upgrade_db_(\d+)\.sql', filename)
            if match:
                version = int(match.group(1))
                migrations.append((version, filepath, filename))

        return sorted(migrations, key=lambda x: x[0])

    def get_available_data_migrations(self):
        """Get all available Python data migrations sorted by version"""
        pattern = os.path.join(self.migrations_dir, 'data_migration_*.py')
        files = glob.glob(pattern)

        migrations = []
        for filepath in files:
            filename = os.path.basename(filepath)
            # Extract version number from filename: data_migration_123.py -> 123
            match = re.match(r'data_migration_(\d+)\.py', filename)
            if match:
                version = int(match.group(1))
                migrations.append((version, filepath, filename))

        return sorted(migrations, key=lambda x: x[0])

    def run_sql_migration(self, version, filepath, filename):
        """Run a single SQL migration file"""
        print(f"  Running SQL migration v{version}: {filename}...")
        start_time = datetime.now()

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = f.read()

            self.cursor.execute(sql)
            self.conn.commit()

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"    ✓ Completed in {execution_time}ms")
            return True

        except Exception as e:
            self.conn.rollback()
            error_msg = str(e)
            if 'already exists' in error_msg.lower():
                print(f"    ⚠ Objects already exist, marking as done")
                return True
            else:
                print(f"    ✗ Error: {error_msg[:200]}")
                return False

    def run_data_migration(self, version, filepath, filename):
        """Run a single Python data migration"""
        print(f"  Running data migration v{version}: {filename}...")
        start_time = datetime.now()

        try:
            # Load and execute the Python module
            spec = importlib.util.spec_from_file_location(f"migration_{version}", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call the migrate function if it exists
            if hasattr(module, 'migrate'):
                module.migrate(self.conn, self.cursor)
                self.conn.commit()

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"    ✓ Completed in {execution_time}ms")
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"    ✗ Error: {str(e)[:200]}")
            return False

    def run_pending_migrations(self):
        """Run all pending migrations"""
        print("\n" + "=" * 60)
        print("DATABASE MIGRATION RUNNER")
        print("=" * 60)

        self.connect()

        try:
            print("\n[1] Checking version table...")
            self.ensure_version_table()
            current_version = self.get_current_version()
            print(f"  Current DB version: {current_version}")

            # Get available migrations
            sql_migrations = self.get_available_migrations()
            data_migrations = self.get_available_data_migrations()

            # Filter pending migrations
            pending_sql = [(v, p, f) for v, p, f in sql_migrations if v > current_version]
            pending_data = [(v, p, f) for v, p, f in data_migrations if v > current_version]

            print(f"\n[2] Available migrations...")
            print(f"  SQL migrations found: {len(sql_migrations)}")
            print(f"  Data migrations found: {len(data_migrations)}")
            print(f"  Pending SQL: {len(pending_sql)}")
            print(f"  Pending Data: {len(pending_data)}")

            if not pending_sql and not pending_data:
                print("\n[3] ✓ Database is up to date!")
            else:
                print(f"\n[3] Running pending migrations...")

                # Combine and sort all pending migrations
                all_pending = []
                for v, p, f in pending_sql:
                    all_pending.append((v, 'sql', p, f))
                for v, p, f in pending_data:
                    all_pending.append((v, 'data', p, f))

                all_pending.sort(key=lambda x: (x[0], 0 if x[1] == 'sql' else 1))

                max_version = current_version
                success_count = 0
                fail_count = 0

                for version, mtype, filepath, filename in all_pending:
                    if mtype == 'sql':
                        success = self.run_sql_migration(version, filepath, filename)
                    else:
                        success = self.run_data_migration(version, filepath, filename)

                    if success:
                        success_count += 1
                        max_version = max(max_version, version)
                    else:
                        fail_count += 1

                # Update version to highest successful migration
                if max_version > current_version:
                    self.set_version(max_version)
                    print(f"\n  Updated DB version: {current_version} -> {max_version}")

                print(f"\n  Results: {success_count} succeeded, {fail_count} failed")

            # Show final status
            final_version = self.get_current_version()
            print(f"\n[4] Final DB version: {final_version}")

            print("\n" + "=" * 60)
            print("MIGRATION COMPLETE")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\n✗ Migration error: {str(e)}")
            self.conn.rollback()
            raise
        finally:
            self.close()


def main():
    runner = MigrationRunner()
    runner.run_pending_migrations()


if __name__ == '__main__':
    main()
