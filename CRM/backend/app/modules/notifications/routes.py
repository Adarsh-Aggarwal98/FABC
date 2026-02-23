"""
Backward compatibility layer - Routes are now in routes/ folder

This file re-exports all route handlers from the new location for backward compatibility.
The routes are automatically registered through the routes/__init__.py import.
"""
# Routes are registered via the routes package import in __init__.py
# This file exists only for backward compatibility with any direct imports
from app.modules.notifications.routes.notification_routes import *
