"""
Audit module services (Backward Compatibility Shim)

This file is maintained for backward compatibility.
All services have been moved to the services/ subfolder.

Import from:
    from app.modules.audit.services import ActivityLogger, AccessLogger, GeolocationService
or:
    from app.modules.audit import ActivityLogger, AccessLogger, GeolocationService
"""
# Re-export all services from the new location using absolute imports
from app.modules.audit.services.activity_logger import ActivityLogger
from app.modules.audit.services.access_logger import AccessLogger
from app.modules.audit.services.geolocation_service import GeolocationService

__all__ = [
    'ActivityLogger',
    'AccessLogger',
    'GeolocationService',
]
