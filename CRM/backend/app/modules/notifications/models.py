"""
Backward compatibility layer - Models are now in models/ folder

This file re-exports all models from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.models import Notification, EmailTemplate, ...
"""
from app.modules.notifications.models.notification import Notification
from app.modules.notifications.models.email_template import EmailTemplate
from app.modules.notifications.models.scheduled_email import ScheduledEmail
from app.modules.notifications.models.email_automation import EmailAutomation, EmailAutomationLog

__all__ = [
    'Notification',
    'EmailTemplate',
    'ScheduledEmail',
    'EmailAutomation',
    'EmailAutomationLog',
]
