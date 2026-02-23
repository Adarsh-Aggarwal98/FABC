#!/bin/bash
# =============================================================================
# Deployment Script for Jaypee CRM
# Usage: ./deploy.sh [options]
#   --full-build:       Force rebuild all containers
#   --backend-only:     Rebuild backend container only
#   --frontend-only:    Rebuild frontend container only
#   --rebuild-db:       Rebuild database (fresh schema + seed_data.sql if exists)
#   --rebuild-db-backup: Rebuild database (fresh schema + restore existing data)
# =============================================================================

set -e  # Exit on any error
set -o pipefail  # Catch errors in piped commands

# Configuration
APP_DIR="/root/Jaypee_crm"
COMPOSE_FILE="docker-compose.deploy.yml"
BACKUP_DIR="/root/Jaypee_crm/backups"
LOG_FILE="/tmp/deploy_$(date +%Y%m%d_%H%M%S).log"
SEED_DATA_FILE="backend/sql_migrations/seed_data.sql"

# Flags
FULL_BUILD=false
BACKEND_ONLY=false
FRONTEND_ONLY=false
REBUILD_DB=false
REBUILD_DB_BACKUP=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --full-build)
            FULL_BUILD=true
            ;;
        --backend-only)
            BACKEND_ONLY=true
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            ;;
        --rebuild-db)
            REBUILD_DB=true
            ;;
        --rebuild-db-backup)
            REBUILD_DB_BACKUP=true
            ;;
    esac
done

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ ERROR: $1" | tee -a "$LOG_FILE"
}

warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ WARNING: $1" | tee -a "$LOG_FILE"
}

# =============================================================================
# Database Backup Function
# =============================================================================
backup_database() {
    log "Creating database backup..."
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"

    # Check if db container is running
    if docker ps --format '{{.Names}}' | grep -q "jaypee-crm-db"; then
        # Check if database exists before backup
        DB_EXISTS=$(docker exec jaypee-crm-db psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='accountant_crm';" 2>/dev/null || echo "")
        if [ "$DB_EXISTS" = "1" ]; then
            docker exec jaypee-crm-db pg_dump -U postgres -d accountant_crm > "$BACKUP_FILE" 2>&1
            if [ $? -eq 0 ]; then
                log "Database backup created: $BACKUP_FILE"
                echo "$BACKUP_FILE"
            else
                warn "Database backup had issues, continuing..."
                echo ""
            fi
        else
            warn "Database 'accountant_crm' does not exist, skipping backup"
            echo ""
        fi
    else
        warn "Database container not running, skipping backup"
        echo ""
    fi
}

# =============================================================================
# Database Restore Function
# =============================================================================
restore_database() {
    local BACKUP_FILE=$1

    if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
        warn "No backup file to restore"
        return
    fi

    log "Waiting for database to be ready..."
    for i in {1..30}; do
        if docker exec jaypee-crm-db pg_isready -U postgres > /dev/null 2>&1; then
            log "Database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            error "Database not ready after 60 seconds"
            exit 1
        fi
        sleep 2
    done

    log "Restoring database from backup..."
    docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm < "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Database restored successfully"
    else
        warn "Database restore completed with warnings"
    fi
}

# =============================================================================
# Main Deployment Process
# =============================================================================

echo "==========================================" | tee -a "$LOG_FILE"
echo "🚀 Starting Deployment Process" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

# Step 1: Navigate to app directory
log "Step 1: Navigating to application directory..."
cd "$APP_DIR" || { error "Failed to navigate to $APP_DIR"; exit 1; }

# Store current commit before pull
OLD_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "none")

# Step 2: Pull latest code from GitHub
log "Step 2: Pulling latest code from GitHub..."
git fetch origin main 2>&1 | tee -a "$LOG_FILE" || { error "Git fetch failed"; exit 1; }
git reset --hard origin/main 2>&1 | tee -a "$LOG_FILE" || { error "Git reset failed"; exit 1; }

NEW_COMMIT=$(git rev-parse HEAD)

# Step 3: Show current git status
log "Step 3: Current Git Status..."
echo "  Branch: $(git branch --show-current)" | tee -a "$LOG_FILE"
echo "  Commit: $(git rev-parse --short HEAD)" | tee -a "$LOG_FILE"
echo "  Message: $(git log -1 --pretty=%B | head -1)" | tee -a "$LOG_FILE"

# Step 4: Verify required files exist
log "Step 4: Verifying required files..."
if [ ! -f "$COMPOSE_FILE" ]; then
    error "docker-compose file not found: $COMPOSE_FILE"
    exit 1
fi
if [ ! -f ".env" ]; then
    error ".env file not found"
    exit 1
fi
log "Required files verified"

# Step 5: Determine what to rebuild
log "Step 5: Determining what to rebuild..."

REBUILD_BACKEND=false
REBUILD_FRONTEND=false

# Check explicit flags first
if [ "$FULL_BUILD" = true ]; then
    log "Full build requested"
    REBUILD_BACKEND=true
    REBUILD_FRONTEND=true
elif [ "$BACKEND_ONLY" = true ]; then
    log "Backend-only build requested"
    REBUILD_BACKEND=true
elif [ "$FRONTEND_ONLY" = true ]; then
    log "Frontend-only build requested"
    REBUILD_FRONTEND=true
else
    # Smart build: Always rebuild both frontend and backend
    log "Smart build: Rebuilding backend + frontend"
    REBUILD_BACKEND=true
    REBUILD_FRONTEND=true
fi

# Step 6: Handle database backup if rebuild with backup requested
DB_BACKUP_FILE=""
if [ "$REBUILD_DB_BACKUP" = true ]; then
    log "Step 6: Database rebuild with backup requested - backing up existing data..."
    DB_BACKUP_FILE=$(backup_database)
elif [ "$REBUILD_DB" = true ]; then
    log "Step 6: Database rebuild requested (fresh schema + seed data if exists)"
else
    log "Step 6: Skipping database rebuild (no --rebuild-db flag)"
fi

# Step 7: Stop containers for rebuild
log "Step 7: Stopping containers for rebuild..."

if [ "$REBUILD_DB" = true ] || [ "$REBUILD_DB_BACKUP" = true ]; then
    # If rebuilding DB, stop and remove everything including volumes
    log "Stopping ALL containers and removing database volume..."
    docker compose -f "$COMPOSE_FILE" down --remove-orphans -v 2>&1 | tee -a "$LOG_FILE" || true
    docker rm -f jaypee-crm-db jaypee-crm-backend jaypee-crm-frontend 2>/dev/null || true
else
    # Preserve database, only stop backend and frontend
    log "Stopping backend and frontend (preserving database)..."
    docker compose -f "$COMPOSE_FILE" stop backend frontend 2>&1 | tee -a "$LOG_FILE" || true
    docker compose -f "$COMPOSE_FILE" rm -f backend frontend 2>&1 | tee -a "$LOG_FILE" || true
    docker rm -f jaypee-crm-backend jaypee-crm-frontend 2>/dev/null || true
fi

# Step 8: Build and deploy application containers
log "Step 8: Building and deploying application containers..."

# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

if [ "$REBUILD_BACKEND" = true ] && [ "$REBUILD_FRONTEND" = true ]; then
    log "Rebuilding all services..."
    docker compose -f "$COMPOSE_FILE" build 2>&1 | tee -a "$LOG_FILE"
    docker compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"
elif [ "$REBUILD_BACKEND" = true ]; then
    log "Rebuilding backend only..."
    docker compose -f "$COMPOSE_FILE" build backend 2>&1 | tee -a "$LOG_FILE"
    docker compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"
elif [ "$REBUILD_FRONTEND" = true ]; then
    log "Rebuilding frontend only..."
    docker compose -f "$COMPOSE_FILE" build frontend 2>&1 | tee -a "$LOG_FILE"
    docker compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"
else
    log "Starting containers..."
    docker compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"
fi

# Step 9: Wait for containers to initialize
log "Step 9: Waiting for containers to initialize (15s)..."
sleep 15

# Step 10: Verify all containers are running
log "Step 10: Verifying container status..."
CONTAINERS=("jaypee-crm-db" "jaypee-crm-backend" "jaypee-crm-frontend")
ALL_RUNNING=true

for container in "${CONTAINERS[@]}"; do
    STATUS=$(docker inspect -f '{{.State.Running}}' "$container" 2>/dev/null || echo "false")
    if [ "$STATUS" = "true" ]; then
        echo "  ✅ $container - RUNNING" | tee -a "$LOG_FILE"
    else
        echo "  ❌ $container - NOT RUNNING" | tee -a "$LOG_FILE"
        echo "--- Container logs for $container ---" | tee -a "$LOG_FILE"
        docker logs "$container" --tail=30 2>&1 | tee -a "$LOG_FILE" || true
        echo "--- End logs ---" | tee -a "$LOG_FILE"
        ALL_RUNNING=false
    fi
done

if [ "$ALL_RUNNING" = false ]; then
    error "Some containers are not running!"
    exit 1
fi

# Step 11: Check database and run migrations
log "Step 11: Checking database and running migrations..."

# Wait for database container to be ready
log "Waiting for database container to be ready..."
for i in {1..30}; do
    if docker exec jaypee-crm-db pg_isready -U postgres > /dev/null 2>&1; then
        log "Database container is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Database container not ready after 60 seconds"
        exit 1
    fi
    sleep 2
done

# Check if database exists, create if not
DB_EXISTS=$(docker exec jaypee-crm-db psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='accountant_crm';" 2>/dev/null || echo "")
if [ "$DB_EXISTS" != "1" ]; then
    log "Database 'accountant_crm' does not exist, creating..."
    docker exec jaypee-crm-db psql -U postgres -c "CREATE DATABASE accountant_crm;" 2>&1 | tee -a "$LOG_FILE"
    log "Database created"
fi

# Check if database schema exists (check for a core table like 'users')
SCHEMA_EXISTS=$(docker exec jaypee-crm-db psql -U postgres -d accountant_crm -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');" 2>/dev/null || echo "false")

if [ "$SCHEMA_EXISTS" != "t" ]; then
    log "Database schema not found, creating from create_db.sql..."
    docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm < backend/sql_migrations/create_db.sql 2>&1 | tee -a "$LOG_FILE"
    if [ $? -eq 0 ]; then
        log "Database schema created successfully"
    else
        warn "Database schema creation had warnings"
    fi

    # Handle data population based on flag
    if [ "$REBUILD_DB_BACKUP" = true ] && [ -n "$DB_BACKUP_FILE" ]; then
        # Restore from backup (--rebuild-db-backup)
        log "Restoring data from backup..."
        # Disable foreign key constraints before import
        log "Disabling foreign key constraints..."
        docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "SET session_replication_role = replica;" 2>&1 | tee -a "$LOG_FILE"
        # Import data
        cat "$DB_BACKUP_FILE" | docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm -c "SET session_replication_role = replica;" -f - 2>&1 | tee -a "$LOG_FILE"
        # Re-enable foreign key constraints
        log "Re-enabling foreign key constraints..."
        docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "SET session_replication_role = DEFAULT;" 2>&1 | tee -a "$LOG_FILE"
        log "Data restored from backup successfully"
    elif [ "$REBUILD_DB" = true ] && [ -f "$SEED_DATA_FILE" ]; then
        # Apply seed data if exists (--rebuild-db)
        log "Found seed_data.sql, applying seed data..."
        # Disable foreign key constraints before import
        log "Disabling foreign key constraints..."
        docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "SET session_replication_role = replica;" 2>&1 | tee -a "$LOG_FILE"
        # Import data
        cat "$SEED_DATA_FILE" | docker exec -i jaypee-crm-db psql -U postgres -d accountant_crm -c "SET session_replication_role = replica;" -f - 2>&1 | tee -a "$LOG_FILE"
        # Re-enable foreign key constraints
        log "Re-enabling foreign key constraints..."
        docker exec jaypee-crm-db psql -U postgres -d accountant_crm -c "SET session_replication_role = DEFAULT;" 2>&1 | tee -a "$LOG_FILE"
        log "Seed data applied successfully"
    elif [ "$REBUILD_DB" = true ]; then
        log "No seed_data.sql found, skipping seed data"
    fi
else
    log "Database schema exists, skipping create_db.sql"
fi

# Initialize default data (roles, etc.) - required before migrations
log "Initializing default data (roles, services)..."
docker exec jaypee-crm-backend flask init-db 2>&1 | tee -a "$LOG_FILE" || warn "init-db completed with warnings"

# Run SQL migrations
log "Running SQL migrations..."
docker exec jaypee-crm-backend python sql_migrations/migration_runner.py 2>&1 | tee -a "$LOG_FILE" || warn "SQL migration completed with warnings"

# Create sample services if needed
log "Creating sample services..."
docker exec jaypee-crm-backend flask create-sample-services 2>&1 | tee -a "$LOG_FILE" || warn "create-sample-services completed with warnings"

# Step 12: Cleanup old images
log "Step 12: Cleaning up old Docker images..."
docker image prune -f 2>&1 | tee -a "$LOG_FILE" || true

# Step 13: Final status
echo "==========================================" | tee -a "$LOG_FILE"
echo "📊 Deployment Summary" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"
echo "Build Type:" | tee -a "$LOG_FILE"
if [ "$FULL_BUILD" = true ]; then
    echo "  🔨 Full Build" | tee -a "$LOG_FILE"
elif [ "$BACKEND_ONLY" = true ]; then
    echo "  🔧 Backend Only" | tee -a "$LOG_FILE"
elif [ "$FRONTEND_ONLY" = true ]; then
    echo "  🎨 Frontend Only" | tee -a "$LOG_FILE"
else
    echo "  🧠 Smart Build" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"
echo "Database:" | tee -a "$LOG_FILE"
if [ "$REBUILD_DB_BACKUP" = true ]; then
    echo "  🔄 Fresh Schema + Restored Backup" | tee -a "$LOG_FILE"
elif [ "$REBUILD_DB" = true ]; then
    if [ -f "$SEED_DATA_FILE" ]; then
        echo "  🌱 Fresh Schema + Seed Data" | tee -a "$LOG_FILE"
    else
        echo "  📋 Fresh Schema Only" | tee -a "$LOG_FILE"
    fi
else
    echo "  ♻️ Existing Database Preserved" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep jaypee | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"
if [ -n "$DB_BACKUP_FILE" ]; then
    echo "💾 Database backup: $DB_BACKUP_FILE" | tee -a "$LOG_FILE"
fi
echo "✅ Deployment completed successfully!" | tee -a "$LOG_FILE"
echo "📄 Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

exit 0
