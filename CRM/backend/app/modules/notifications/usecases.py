"""
Backward compatibility layer - Use cases are now in usecases/ folder

This file re-exports all use cases from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.usecases import CreateScheduledEmailUseCase, ...
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
    'CreateScheduledEmailUseCase',
    'UpdateScheduledEmailUseCase',
    'CancelScheduledEmailUseCase',
    'ListScheduledEmailsUseCase',
    'GetScheduledEmailUseCase',
    'CreateEmailAutomationUseCase',
    'UpdateEmailAutomationUseCase',
    'DeleteEmailAutomationUseCase',
    'ListEmailAutomationsUseCase',
    'GetEmailAutomationUseCase',
    'GetAutomationLogsUseCase',
    'TriggerAutomationUseCase',
]
