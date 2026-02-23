"""
Prometheus Metrics Module for Pointers Consulting CRM

Provides comprehensive monitoring including:
- HTTP request/response metrics (latency, size, status codes)
- System metrics (CPU, memory, disk)
- Application-specific metrics (active users, database connections)
- Business metrics (requests created, invoices generated)
"""

import time
import psutil
import threading
from functools import wraps
from flask import request, g, Response
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    multiprocess, REGISTRY
)


# =============================================================================
# METRIC DEFINITIONS
# =============================================================================

# Request/Response Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000]
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status_code'],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000]
)

# Status Code Buckets (for easier alerting)
STATUS_2XX = Counter(
    'http_requests_2xx_total',
    'Total 2xx HTTP responses',
    ['method', 'endpoint']
)

STATUS_4XX = Counter(
    'http_requests_4xx_total',
    'Total 4xx HTTP responses (client errors)',
    ['method', 'endpoint']
)

STATUS_5XX = Counter(
    'http_requests_5xx_total',
    'Total 5xx HTTP responses (server errors)',
    ['method', 'endpoint']
)

# In-Progress Requests
REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)

# System Metrics
CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'Current CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'Current memory usage in bytes'
)

MEMORY_USAGE_PERCENT = Gauge(
    'system_memory_usage_percent',
    'Current memory usage percentage'
)

MEMORY_AVAILABLE = Gauge(
    'system_memory_available_bytes',
    'Available memory in bytes'
)

DISK_USAGE_PERCENT = Gauge(
    'system_disk_usage_percent',
    'Disk usage percentage',
    ['mount_point']
)

OPEN_FILE_DESCRIPTORS = Gauge(
    'app_open_file_descriptors',
    'Number of open file descriptors'
)

PROCESS_CPU_PERCENT = Gauge(
    'process_cpu_usage_percent',
    'Process CPU usage percentage'
)

PROCESS_MEMORY_BYTES = Gauge(
    'process_memory_bytes',
    'Process memory usage in bytes'
)

PROCESS_THREADS = Gauge(
    'process_threads_total',
    'Number of threads in the process'
)

# Database Metrics
DB_QUERY_COUNT = Counter(
    'database_queries_total',
    'Total database queries executed',
    ['operation']  # SELECT, INSERT, UPDATE, DELETE
)

DB_QUERY_LATENCY = Histogram(
    'database_query_duration_seconds',
    'Database query latency in seconds',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

DB_CONNECTION_POOL_SIZE = Gauge(
    'database_connection_pool_size',
    'Database connection pool size'
)

DB_CONNECTIONS_ACTIVE = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

# Application Metrics
ACTIVE_USERS = Gauge(
    'app_active_users_total',
    'Number of currently active/logged-in users'
)

TOTAL_USERS = Gauge(
    'app_total_users',
    'Total number of registered users'
)

TOTAL_CLIENTS = Gauge(
    'app_total_clients',
    'Total number of client users'
)

# Business Metrics
SERVICE_REQUESTS_CREATED = Counter(
    'business_service_requests_created_total',
    'Total service requests created',
    ['service_type', 'status']
)

INVOICES_GENERATED = Counter(
    'business_invoices_generated_total',
    'Total invoices generated',
    ['status']  # paid, unpaid, overdue
)

SUBMISSIONS_RECEIVED = Counter(
    'business_submissions_received_total',
    'Total form/assessment submissions received',
    ['form_type']
)

# Error Tracking
EXCEPTIONS_TOTAL = Counter(
    'app_exceptions_total',
    'Total exceptions raised',
    ['exception_type', 'endpoint']
)

# Authentication Metrics
AUTH_LOGIN_ATTEMPTS = Counter(
    'auth_login_attempts_total',
    'Total login attempts',
    ['status']  # success, failure
)

AUTH_TOKEN_OPERATIONS = Counter(
    'auth_token_operations_total',
    'Total token operations',
    ['operation']  # issued, refreshed, revoked, expired
)

# App Info
APP_INFO = Info(
    'app',
    'Application information'
)


# =============================================================================
# METRICS COLLECTION FUNCTIONS
# =============================================================================

def collect_system_metrics():
    """Collect system-level metrics"""
    try:
        # CPU
        CPU_USAGE.set(psutil.cpu_percent(interval=None))

        # Memory
        memory = psutil.virtual_memory()
        MEMORY_USAGE.set(memory.used)
        MEMORY_USAGE_PERCENT.set(memory.percent)
        MEMORY_AVAILABLE.set(memory.available)

        # Disk
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                DISK_USAGE_PERCENT.labels(mount_point=partition.mountpoint).set(usage.percent)
            except (PermissionError, OSError):
                pass

        # Process-specific metrics
        process = psutil.Process()
        PROCESS_CPU_PERCENT.set(process.cpu_percent())
        PROCESS_MEMORY_BYTES.set(process.memory_info().rss)
        PROCESS_THREADS.set(process.num_threads())

        try:
            OPEN_FILE_DESCRIPTORS.set(process.num_fds())
        except AttributeError:
            # Windows doesn't support num_fds
            pass

    except Exception as e:
        print(f"Error collecting system metrics: {e}")


def start_metrics_collector(interval=15):
    """Start background thread to collect system metrics periodically"""
    def collector():
        while True:
            collect_system_metrics()
            time.sleep(interval)

    thread = threading.Thread(target=collector, daemon=True)
    thread.start()


# =============================================================================
# MIDDLEWARE / DECORATORS
# =============================================================================

def init_metrics(app):
    """Initialize Prometheus metrics for Flask app"""

    # Set app info
    APP_INFO.info({
        'version': '1.0.0',
        'environment': app.config.get('ENV', 'production'),
        'app_name': 'pointers-crm'
    })

    # Start system metrics collector
    start_metrics_collector()

    @app.before_request
    def before_request():
        """Record request start time and increment in-progress counter"""
        g.start_time = time.time()
        g.request_size = request.content_length or 0

        endpoint = get_endpoint_label()
        REQUESTS_IN_PROGRESS.labels(
            method=request.method,
            endpoint=endpoint
        ).inc()

    @app.after_request
    def after_request(response):
        """Record request metrics"""
        try:
            # Calculate request duration
            request_latency = time.time() - getattr(g, 'start_time', time.time())

            endpoint = get_endpoint_label()
            method = request.method
            status_code = str(response.status_code)

            # Request count and latency
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(request_latency)

            # Request size
            request_size = getattr(g, 'request_size', 0)
            REQUEST_SIZE.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)

            # Response size
            response_size = response.content_length or len(response.get_data())
            RESPONSE_SIZE.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(response_size)

            # Status code buckets
            if response.status_code >= 200 and response.status_code < 300:
                STATUS_2XX.labels(method=method, endpoint=endpoint).inc()
            elif response.status_code >= 400 and response.status_code < 500:
                STATUS_4XX.labels(method=method, endpoint=endpoint).inc()
            elif response.status_code >= 500:
                STATUS_5XX.labels(method=method, endpoint=endpoint).inc()

            # Decrement in-progress counter
            REQUESTS_IN_PROGRESS.labels(
                method=method,
                endpoint=endpoint
            ).dec()

        except Exception as e:
            app.logger.error(f"Error recording metrics: {e}")

        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Track exceptions"""
        endpoint = get_endpoint_label()
        EXCEPTIONS_TOTAL.labels(
            exception_type=type(e).__name__,
            endpoint=endpoint
        ).inc()
        raise e

    # Metrics endpoint
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        # Collect latest system metrics before returning
        collect_system_metrics()
        return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

    app.logger.info("Prometheus metrics initialized")


def get_endpoint_label():
    """Get a clean endpoint label for metrics (without dynamic parts)"""
    if request.url_rule:
        # Use the URL rule pattern (e.g., /api/users/<id> instead of /api/users/123)
        return request.url_rule.rule
    return request.path


# =============================================================================
# BUSINESS METRIC HELPERS
# =============================================================================

def track_service_request(service_type, status='pending'):
    """Track when a service request is created"""
    SERVICE_REQUESTS_CREATED.labels(service_type=service_type, status=status).inc()


def track_invoice(status='unpaid'):
    """Track when an invoice is generated"""
    INVOICES_GENERATED.labels(status=status).inc()


def track_submission(form_type='generic'):
    """Track when a form submission is received"""
    SUBMISSIONS_RECEIVED.labels(form_type=form_type).inc()


def track_login(success=True):
    """Track login attempts"""
    status = 'success' if success else 'failure'
    AUTH_LOGIN_ATTEMPTS.labels(status=status).inc()


def track_token_operation(operation):
    """Track token operations (issued, refreshed, revoked, expired)"""
    AUTH_TOKEN_OPERATIONS.labels(operation=operation).inc()


def update_active_users(count):
    """Update the number of active users"""
    ACTIVE_USERS.set(count)


def update_total_users(total, clients):
    """Update total user counts"""
    TOTAL_USERS.set(total)
    TOTAL_CLIENTS.set(clients)


def track_db_query(operation, duration):
    """Track database query metrics"""
    DB_QUERY_COUNT.labels(operation=operation).inc()
    DB_QUERY_LATENCY.labels(operation=operation).observe(duration)


def update_db_pool_stats(pool_size, active_connections):
    """Update database connection pool stats"""
    DB_CONNECTION_POOL_SIZE.set(pool_size)
    DB_CONNECTIONS_ACTIVE.set(active_connections)
