"""
Geolocation Service (Backward Compatibility Shim)

This file is maintained for backward compatibility.
The GeolocationService has been moved to the services/ subfolder.

Import from:
    from app.modules.audit.services import GeolocationService
or:
    from app.modules.audit import GeolocationService
"""
# Re-export from the new location using absolute import
from app.modules.audit.services.geolocation_service import GeolocationService

__all__ = ['GeolocationService']
