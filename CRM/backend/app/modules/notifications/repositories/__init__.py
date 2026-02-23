"""
Notification Repositories Package
"""
from app.modules.notifications.repositories.notification_repository import NotificationRepository
from app.modules.notifications.repositories.email_template_repository import EmailTemplateRepository

__all__ = [
    'NotificationRepository',
    'EmailTemplateRepository',
]
