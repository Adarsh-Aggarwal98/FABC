"""
Backward compatibility layer - Schemas are now in schemas/ folder

This file re-exports all schemas from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.schemas import ScheduledEmailSchema, ...
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
