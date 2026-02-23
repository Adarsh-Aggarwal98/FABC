"""
Services Routes Package

This module registers all route blueprints for the services module.
"""
from flask import Blueprint

# Create blueprints
services_bp = Blueprint('services', __name__)
requests_bp = Blueprint('requests', __name__)

# Import routes to register them with blueprints
from . import service_routes  # noqa: E402, F401
from . import request_routes  # noqa: E402, F401
from . import query_routes  # noqa: E402, F401
from . import analytics_routes  # noqa: E402, F401

# Import workflow blueprint
from .workflow_routes import workflow_bp  # noqa: E402

# Import renewal blueprint
from .renewal_routes import renewals_bp  # noqa: E402

# Import status blueprint
from .status_routes import status_bp  # noqa: E402

# Import invoice blueprint
from .invoice_routes import invoices_bp  # noqa: E402

# Import task blueprint
from .task_routes import task_bp  # noqa: E402

# Import client pricing blueprint
from .client_pricing_routes import client_pricing_bp  # noqa: E402

__all__ = ['services_bp', 'requests_bp', 'workflow_bp', 'renewals_bp', 'status_bp', 'invoices_bp', 'task_bp', 'client_pricing_bp']
