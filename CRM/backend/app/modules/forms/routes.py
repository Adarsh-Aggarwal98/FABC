"""
Forms Routes - Backward Compatibility Layer
============================================

This file provides backward compatibility for imports from the old flat structure.
All routes have been moved to the routes/ folder.

The routes are now defined in routes/form_routes.py and automatically
registered with the forms_bp blueprint via the routes/__init__.py.
"""
# Re-export from the new location for backward compatibility
from app.modules.forms.routes.form_routes import *
