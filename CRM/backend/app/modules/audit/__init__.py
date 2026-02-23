"""
Audit Module - Clean Architecture

This module provides audit logging, activity tracking, access logging,
and user impersonation functionality.

Structure:
    models/         - Database models (ActivityLog, AccessLog, ImpersonationSession)
    services/       - Business logic services (ActivityLogger, AccessLogger, GeolocationService)
    routes/         - API endpoints
    repositories.py - Data access layer
    usecases.py     - Use case implementations
    constants.py    - Module constants
    decorators.py   - Activity logging decorators

Backward Compatibility:
    All exports from the old flat structure are maintained for backward compatibility.
    You can import directly from the module:
        from app.modules.audit import ActivityLog, ActivityLogger, etc.
"""
from flask import Blueprint

# Create blueprint
audit_bp = Blueprint('audit', __name__)

# Import models directly from subfolder
from .models.audit_log import ActivityLog, ImpersonationSession  # noqa: E402
from .models.access_log import AccessLog  # noqa: E402

# Import services directly from subfolder
from .services.activity_logger import ActivityLogger  # noqa: E402
from .services.access_logger import AccessLogger  # noqa: E402
from .services.geolocation_service import GeolocationService  # noqa: E402

# Import routes to register endpoints (must be after blueprint creation)
from .routes import audit_routes  # noqa: E402, F401

# Re-export constants for backward compatibility
from .constants import (  # noqa: E402
    ACTION_CREATED,
    ACTION_UPDATED,
    ACTION_DELETED,
    ACTION_ASSIGNED,
    ACTION_UNASSIGNED,
    ACTION_STATUS_CHANGED,
    ACTION_LOGIN,
    ACTION_LOGOUT,
    ACTION_PASSWORD_CHANGED,
    ACTION_INVITED,
    ACTION_ACTIVATED,
    ACTION_DEACTIVATED,
    ACTION_DOCUMENT_UPLOADED,
    ACTION_DOCUMENT_DOWNLOADED,
    ACTION_NOTE_ADDED,
    ACTION_TAG_ASSIGNED,
    ACTION_TAG_REMOVED,
    ACTION_INVOICE_RAISED,
    ACTION_INVOICE_PAID,
    ACTION_FORM_SUBMITTED,
    ACTION_EMAIL_SENT,
    ENTITY_USER,
    ENTITY_SERVICE_REQUEST,
    ENTITY_DOCUMENT,
    ENTITY_COMPANY,
    ENTITY_TAG,
    ENTITY_NOTE,
    ENTITY_FORM,
    ENTITY_EMAIL_TEMPLATE,
    ENTITY_SERVICE,
)

# Re-export decorators for backward compatibility
from .decorators import log_activity  # noqa: E402

# Re-export repositories for backward compatibility
from .repositories import ActivityLogRepository  # noqa: E402

# Re-export usecases for backward compatibility
from .usecases import (  # noqa: E402
    GetEntityActivityUseCase,
    GetUserActivityUseCase,
    GetCompanyActivityUseCase,
    SearchActivityUseCase,
    StartImpersonationUseCase,
    StopImpersonationUseCase,
    GetImpersonationHistoryUseCase,
    GetMyActiveImpersonationUseCase,
)

__all__ = [
    # Blueprint
    'audit_bp',

    # Models
    'ActivityLog',
    'ImpersonationSession',
    'AccessLog',

    # Services
    'ActivityLogger',
    'AccessLogger',
    'GeolocationService',

    # Repositories
    'ActivityLogRepository',

    # Use Cases
    'GetEntityActivityUseCase',
    'GetUserActivityUseCase',
    'GetCompanyActivityUseCase',
    'SearchActivityUseCase',
    'StartImpersonationUseCase',
    'StopImpersonationUseCase',
    'GetImpersonationHistoryUseCase',
    'GetMyActiveImpersonationUseCase',

    # Decorators
    'log_activity',

    # Action Constants
    'ACTION_CREATED',
    'ACTION_UPDATED',
    'ACTION_DELETED',
    'ACTION_ASSIGNED',
    'ACTION_UNASSIGNED',
    'ACTION_STATUS_CHANGED',
    'ACTION_LOGIN',
    'ACTION_LOGOUT',
    'ACTION_PASSWORD_CHANGED',
    'ACTION_INVITED',
    'ACTION_ACTIVATED',
    'ACTION_DEACTIVATED',
    'ACTION_DOCUMENT_UPLOADED',
    'ACTION_DOCUMENT_DOWNLOADED',
    'ACTION_NOTE_ADDED',
    'ACTION_TAG_ASSIGNED',
    'ACTION_TAG_REMOVED',
    'ACTION_INVOICE_RAISED',
    'ACTION_INVOICE_PAID',
    'ACTION_FORM_SUBMITTED',
    'ACTION_EMAIL_SENT',

    # Entity Constants
    'ENTITY_USER',
    'ENTITY_SERVICE_REQUEST',
    'ENTITY_DOCUMENT',
    'ENTITY_COMPANY',
    'ENTITY_TAG',
    'ENTITY_NOTE',
    'ENTITY_FORM',
    'ENTITY_EMAIL_TEMPLATE',
    'ENTITY_SERVICE',
]
