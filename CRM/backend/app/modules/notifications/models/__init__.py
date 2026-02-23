"""
Notification Models Package
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
