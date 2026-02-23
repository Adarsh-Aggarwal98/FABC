"""
Notification Services Package

For backward compatibility, NotificationService is an alias for EmailService
which contains all the email sending functionality that was previously in NotificationService.
"""
from app.modules.notifications.services.notification_service import NotificationService as InAppNotificationService
from app.modules.notifications.services.email_service import EmailService
from app.modules.notifications.services.bulk_email_service import BulkEmailRecipientService

# For backward compatibility, NotificationService is aliased to EmailService
# The original NotificationService had both email and in-app notification methods
# Now EmailService contains all email-related methods, and we expose it as NotificationService
# to maintain backward compatibility with existing imports
NotificationService = EmailService

__all__ = [
    'NotificationService',  # Backward compatible alias (points to EmailService)
    'EmailService',         # Email-specific service
    'InAppNotificationService',  # In-app notification service
    'BulkEmailRecipientService',  # Bulk email filtering service
]
