"""
Notification Schemas Package
"""
from app.modules.notifications.schemas.scheduled_email_schemas import (
    ScheduledEmailSchema,
    UpdateScheduledEmailSchema,
)
from app.modules.notifications.schemas.email_automation_schemas import (
    EmailAutomationSchema,
    UpdateEmailAutomationSchema,
)
from app.modules.notifications.schemas.recipient_filter_schemas import RecipientFilterSchema

__all__ = [
    'ScheduledEmailSchema',
    'UpdateScheduledEmailSchema',
    'EmailAutomationSchema',
    'UpdateEmailAutomationSchema',
    'RecipientFilterSchema',
]
