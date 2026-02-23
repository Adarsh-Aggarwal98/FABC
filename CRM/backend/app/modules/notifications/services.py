"""
Backward compatibility layer - Services are now in services/ folder

This file re-exports all services from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.services import NotificationService, ...
"""
from app.modules.notifications.services.email_service import EmailService
from app.modules.notifications.services.bulk_email_service import BulkEmailRecipientService

# For backward compatibility, NotificationService is aliased to EmailService
NotificationService = EmailService

__all__ = [
    'NotificationService',
    'EmailService',
    'BulkEmailRecipientService',
]
