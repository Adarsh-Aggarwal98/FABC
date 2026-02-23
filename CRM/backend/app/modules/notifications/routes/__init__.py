"""
Notification Routes Package
"""
# Import routes to register them with the blueprint
from app.modules.notifications.routes import notification_routes

__all__ = ['notification_routes']
