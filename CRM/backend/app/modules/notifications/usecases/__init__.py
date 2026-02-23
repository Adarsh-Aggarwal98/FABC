"""
Notification Use Cases Package
"""
from app.modules.notifications.usecases.base import UseCaseResult
from app.modules.notifications.usecases.scheduled_email_usecases import (
    CreateScheduledEmailUseCase,
    UpdateScheduledEmailUseCase,
    CancelScheduledEmailUseCase,
    ListScheduledEmailsUseCase,
    GetScheduledEmailUseCase,
)
from app.modules.notifications.usecases.email_automation_usecases import (
    CreateEmailAutomationUseCase,
    UpdateEmailAutomationUseCase,
    DeleteEmailAutomationUseCase,
    ListEmailAutomationsUseCase,
    GetEmailAutomationUseCase,
    GetAutomationLogsUseCase,
    TriggerAutomationUseCase,
)

__all__ = [
    'UseCaseResult',
    # Scheduled Email Use Cases
    'CreateScheduledEmailUseCase',
    'UpdateScheduledEmailUseCase',
    'CancelScheduledEmailUseCase',
    'ListScheduledEmailsUseCase',
    'GetScheduledEmailUseCase',
    # Email Automation Use Cases
    'CreateEmailAutomationUseCase',
    'UpdateEmailAutomationUseCase',
    'DeleteEmailAutomationUseCase',
    'ListEmailAutomationsUseCase',
    'GetEmailAutomationUseCase',
    'GetAutomationLogsUseCase',
    'TriggerAutomationUseCase',
]
