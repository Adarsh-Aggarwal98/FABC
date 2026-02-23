"""
Audit module routes (Backward Compatibility Shim)

This file is maintained for backward compatibility.
All routes have been moved to the routes/ subfolder.

The routes are automatically registered when the module is imported.
"""
# Import routes to ensure they are registered
from .routes import audit_routes  # noqa: F401

# Note: All route functions are registered on audit_bp through the routes/audit_routes.py module
