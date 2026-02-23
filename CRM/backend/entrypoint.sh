#!/bin/sh

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Remove old migrations if they exist but are incomplete
if [ -d "migrations" ] && [ ! -f "migrations/env.py" ]; then
    echo "Removing incomplete migrations folder..."
    rm -rf migrations
fi

# Initialize migrations if not exists
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
fi

# Always try to create a new migration (will be skipped if no changes)
echo "Checking for model changes..."
flask db migrate -m "Auto migration $(date +%Y%m%d_%H%M%S)" 2>/dev/null || echo "No new migrations needed or migration already exists"

echo "Applying database migrations..."
flask db upgrade || {
    echo "Migration upgrade failed, trying to create tables directly..."
    python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Tables created successfully!')"
}

# Run versioned SQL migrations (data migrations, schema updates)
echo "Running versioned SQL migrations..."
python sql_migrations/migration_runner.py || echo "SQL migrations had issues, continuing..."

# Initialize default data
echo "Initializing default data..."
flask init-db || echo "init-db had issues, continuing..."
flask create-sample-services || echo "create-sample-services had issues, continuing..."
flask create-demo-data || echo "create-demo-data had issues, continuing..."

echo "Starting Flask server with Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - --capture-output --log-level info --reload "app:create_app()"
