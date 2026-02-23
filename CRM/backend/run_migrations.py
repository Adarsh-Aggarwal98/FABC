#!/usr/bin/env python3
"""
Migration Script - Run missing database migrations
This script checks for missing columns and tables, then applies necessary migrations.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection settings
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'accountant_crm'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres')
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def check_column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        )
    """, (table, column))
    return cursor.fetchone()[0]

def check_table_exists(cursor, table):
    """Check if a table exists"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = %s
        )
    """, (table,))
    return cursor.fetchone()[0]

def get_row_count(cursor, table):
    """Get row count of a table"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]
    except:
        return 0

def run_migration_file(cursor, filepath):
    """Run a SQL migration file"""
    print(f"  Running: {os.path.basename(filepath)}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        cursor.execute(sql)
        print(f"    ✓ Success")
        return True
    except Exception as e:
        print(f"    ✗ Error: {str(e)[:100]}")
        return False

def main():
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 60)

    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()

    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    try:
        # ============================================
        # STEP 1: Check current state
        # ============================================
        print("\n[1] Checking current database state...")

        # Check missing columns
        missing_columns = []

        columns_to_check = [
            ('service_requests', 'current_step_id'),
            ('services', 'workflow_id'),
            ('queries', 'is_internal'),
        ]

        for table, column in columns_to_check:
            if check_table_exists(cursor, table):
                if not check_column_exists(cursor, table, column):
                    missing_columns.append((table, column))
                    print(f"  Missing: {table}.{column}")
                else:
                    print(f"  Exists: {table}.{column}")

        # Check workflow data
        workflow_steps_count = get_row_count(cursor, 'workflow_steps')
        print(f"  workflow_steps rows: {workflow_steps_count}")

        # ============================================
        # STEP 2: Add missing columns
        # ============================================
        print("\n[2] Adding missing columns...")

        # Add current_step_id to service_requests
        if ('service_requests', 'current_step_id') in missing_columns:
            print("  Adding service_requests.current_step_id...")
            cursor.execute("""
                ALTER TABLE service_requests
                ADD COLUMN IF NOT EXISTS current_step_id VARCHAR(36)
                REFERENCES workflow_steps(id) ON DELETE SET NULL
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_service_requests_step
                ON service_requests(current_step_id)
            """)
            print("    ✓ Added")

        # Add workflow_id to services
        if ('services', 'workflow_id') in missing_columns:
            print("  Adding services.workflow_id...")
            cursor.execute("""
                ALTER TABLE services
                ADD COLUMN IF NOT EXISTS workflow_id VARCHAR(36)
                REFERENCES service_workflows(id) ON DELETE SET NULL
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_services_workflow
                ON services(workflow_id)
            """)
            print("    ✓ Added")

        # Add is_internal to queries if table exists
        if check_table_exists(cursor, 'queries'):
            if ('queries', 'is_internal') in missing_columns:
                print("  Adding queries.is_internal...")
                cursor.execute("""
                    ALTER TABLE queries
                    ADD COLUMN IF NOT EXISTS is_internal BOOLEAN DEFAULT FALSE
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queries_is_internal
                    ON queries(is_internal)
                """)
                print("    ✓ Added")

        conn.commit()

        # ============================================
        # STEP 3: Seed workflow data if missing
        # ============================================
        print("\n[3] Checking workflow data...")

        if workflow_steps_count == 0:
            print("  No workflow steps found. Seeding default workflow...")

            # Check if service_workflows has default workflow
            cursor.execute("SELECT COUNT(*) FROM service_workflows WHERE id = 'default-workflow'")
            if cursor.fetchone()[0] == 0:
                print("  Inserting default workflow...")
                cursor.execute("""
                    INSERT INTO service_workflows (id, name, description, is_default, is_active)
                    VALUES ('default-workflow', 'Default Workflow', 'Standard service request workflow', TRUE, TRUE)
                    ON CONFLICT (id) DO NOTHING
                """)

            # Insert default steps
            print("  Inserting workflow steps...")
            cursor.execute("""
                INSERT INTO workflow_steps (id, workflow_id, name, display_name, step_type, "order", color, position_x, position_y) VALUES
                ('step-pending', 'default-workflow', 'pending', 'Pending', 'START', 1, 'gray', 100, 100),
                ('step-invoice-raised', 'default-workflow', 'invoice_raised', 'Invoice Raised', 'NORMAL', 2, 'blue', 300, 100),
                ('step-assigned', 'default-workflow', 'assigned', 'Assigned', 'NORMAL', 3, 'indigo', 500, 100),
                ('step-processing', 'default-workflow', 'processing', 'Processing', 'NORMAL', 4, 'yellow', 700, 100),
                ('step-query-raised', 'default-workflow', 'query_raised', 'Query Raised', 'QUERY', 5, 'orange', 700, 250),
                ('step-review', 'default-workflow', 'accountant_review_pending', 'Under Review', 'NORMAL', 6, 'purple', 500, 250),
                ('step-admin-review', 'default-workflow', 'admin_review', 'Admin Review', 'NORMAL', 7, 'purple', 900, 250),
                ('step-completed', 'default-workflow', 'completed', 'Completed', 'END', 8, 'green', 1100, 100)
                ON CONFLICT (id) DO NOTHING
            """)

            # Insert default transitions
            print("  Inserting workflow transitions...")
            cursor.execute("""
                INSERT INTO workflow_transitions (id, workflow_id, from_step_id, to_step_id, name, allowed_roles) VALUES
                ('trans-1', 'default-workflow', 'step-pending', 'step-invoice-raised', 'Raise Invoice', '["admin", "super_admin"]'),
                ('trans-2', 'default-workflow', 'step-invoice-raised', 'step-assigned', 'Assign', '["admin", "super_admin"]'),
                ('trans-3', 'default-workflow', 'step-assigned', 'step-processing', 'Start Processing', '["accountant", "admin", "super_admin"]'),
                ('trans-4', 'default-workflow', 'step-processing', 'step-query-raised', 'Raise Query', '["accountant", "admin", "super_admin"]'),
                ('trans-5', 'default-workflow', 'step-query-raised', 'step-review', 'Client Responded', '["user"]'),
                ('trans-6', 'default-workflow', 'step-review', 'step-processing', 'Resume Work', '["accountant", "admin", "super_admin"]'),
                ('trans-7', 'default-workflow', 'step-processing', 'step-completed', 'Complete', '["accountant", "admin", "super_admin"]'),
                ('trans-8', 'default-workflow', 'step-processing', 'step-admin-review', 'Submit for Admin Review', '["accountant", "admin", "super_admin"]'),
                ('trans-9', 'default-workflow', 'step-admin-review', 'step-processing', 'Request Changes', '["admin", "super_admin"]'),
                ('trans-10', 'default-workflow', 'step-admin-review', 'step-completed', 'Approve & Complete', '["admin", "super_admin"]')
                ON CONFLICT (id) DO NOTHING
            """)

            conn.commit()
            print("    ✓ Workflow data seeded")

        # ============================================
        # STEP 4: Update existing service_requests
        # ============================================
        print("\n[4] Updating existing service requests with workflow steps...")

        cursor.execute("""
            UPDATE service_requests sr
            SET current_step_id =
                CASE status
                    WHEN 'pending' THEN 'step-pending'
                    WHEN 'invoice_raised' THEN 'step-invoice-raised'
                    WHEN 'assigned' THEN 'step-assigned'
                    WHEN 'processing' THEN 'step-processing'
                    WHEN 'query_raised' THEN 'step-query-raised'
                    WHEN 'accountant_review_pending' THEN 'step-review'
                    WHEN 'admin_review' THEN 'step-admin-review'
                    WHEN 'completed' THEN 'step-completed'
                    ELSE 'step-pending'
                END
            WHERE current_step_id IS NULL
        """)
        updated_count = cursor.rowcount
        print(f"  Updated {updated_count} service requests")

        conn.commit()

        # ============================================
        # STEP 5: Run additional migration files
        # ============================================
        print("\n[5] Running additional migration files...")

        migration_files = [
            'seed_service_workflows.sql',
        ]

        for filename in migration_files:
            filepath = os.path.join(migrations_dir, filename)
            if os.path.exists(filepath):
                run_migration_file(cursor, filepath)
                conn.commit()

        # ============================================
        # STEP 6: Final verification
        # ============================================
        print("\n[6] Final verification...")

        # Check columns again
        for table, column in columns_to_check:
            if check_table_exists(cursor, table):
                exists = check_column_exists(cursor, table, column)
                status = "✓" if exists else "✗"
                print(f"  {status} {table}.{column}")

        # Check workflow data
        cursor.execute("SELECT COUNT(*) FROM workflow_steps")
        steps_count = cursor.fetchone()[0]
        print(f"  workflow_steps: {steps_count} rows")

        cursor.execute("SELECT COUNT(*) FROM workflow_transitions")
        trans_count = cursor.fetchone()[0]
        print(f"  workflow_transitions: {trans_count} rows")

        cursor.execute("SELECT COUNT(*) FROM service_requests WHERE current_step_id IS NOT NULL")
        requests_with_step = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM service_requests")
        total_requests = cursor.fetchone()[0]
        print(f"  service_requests with step: {requests_with_step}/{total_requests}")

        conn.commit()

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during migration: {str(e)}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
