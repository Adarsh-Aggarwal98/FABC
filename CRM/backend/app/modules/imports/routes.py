"""
Data Import Routes - Backward Compatibility Module

This file maintains backward compatibility for existing imports.
The actual implementation has been moved to routes/import_routes.py.

For new code, prefer importing from:
    from app.modules.imports.routes import import_bp

Or from the main module:
    from app.modules.imports import import_bp
"""
# Re-export everything from the new routes module for backward compatibility
from app.modules.imports.routes.import_routes import (
    import_bp,
    download_template,
    import_clients,
    import_service_requests,
    import_services,
    import_companies,
    get_available_import_types,
    get_current_user
)

__all__ = [
    'import_bp',
    'download_template',
    'import_clients',
    'import_service_requests',
    'import_services',
    'import_companies',
    'get_available_import_types',
    'get_current_user'
]
