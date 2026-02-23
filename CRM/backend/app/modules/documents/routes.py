"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.routes import *

The actual routes are now in app.modules.documents.routes.document_routes
"""
# Import all route handlers from the new location
# This registers them with the blueprint when this module is imported
from app.modules.documents.routes.document_routes import *
