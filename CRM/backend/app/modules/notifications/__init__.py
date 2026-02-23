"""
Notifications Module
====================

Clean architecture module for handling notifications including:
- In-app notifications
- Email notifications (multiple providers)
- Email templates
- Scheduled emails
- Email automations

Structure:
---------
- models/       - Database models (Notification, EmailTemplate, ScheduledEmail, EmailAutomation)
- repositories/ - Data access layer (NotificationRepository, EmailTemplateRepository)
- services/     - Business services (NotificationService, EmailService, BulkEmailRecipientService)
- usecases/     - Use case implementations
- schemas/      - Validation schemas (Marshmallow)
- routes/       - API endpoints
- clients/      - Email provider clients (SMTP, Graph, MailerSend, SendGrid)

Backward Compatibility:
----------------------
All models, services, and clients are re-exported at the module level
to maintain backward compatibility with existing imports.

NotificationService is aliased to EmailService for backward compatibility.
"""
from flask import Blueprint

# Create the blueprint
notifications_bp = Blueprint('notifications', __name__)

# Import routes to register them
from app.modules.notifications.routes import notification_routes  # noqa: E402, F401

# ============== Backward Compatibility Exports ==============

# Models - Export at module level for backward compatibility
from app.modules.notifications.models import (  # noqa: E402
    Notification,
    EmailTemplate,
    ScheduledEmail,
    EmailAutomation,
    EmailAutomationLog,
)

# Services - Export at module level for backward compatibility
# NotificationService is an alias for EmailService for backward compatibility
from app.modules.notifications.services import (  # noqa: E402
    NotificationService,  # Backward compatible alias (points to EmailService)
    EmailService,
    BulkEmailRecipientService,
)

# Clients - Export at module level for backward compatibility
from app.modules.notifications.clients import (  # noqa: E402
    GraphAPIClient,
    SMTPClient,
    EmailClientFactory,
    MailerSendClient,
    SendGridClient,
)

# Schemas - Export at module level for backward compatibility
from app.modules.notifications.schemas import (  # noqa: E402
    ScheduledEmailSchema,
    UpdateScheduledEmailSchema,
    EmailAutomationSchema,
    UpdateEmailAutomationSchema,
    RecipientFilterSchema,
)

# Use Cases - Export at module level for backward compatibility
from app.modules.notifications.usecases import (  # noqa: E402
    UseCaseResult,
    CreateScheduledEmailUseCase,
    UpdateScheduledEmailUseCase,
    CancelScheduledEmailUseCase,
    ListScheduledEmailsUseCase,
    GetScheduledEmailUseCase,
    CreateEmailAutomationUseCase,
    UpdateEmailAutomationUseCase,
    DeleteEmailAutomationUseCase,
    ListEmailAutomationsUseCase,
    GetEmailAutomationUseCase,
    GetAutomationLogsUseCase,
    TriggerAutomationUseCase,
)

# Repositories
from app.modules.notifications.repositories import (  # noqa: E402
    NotificationRepository,
    EmailTemplateRepository,
)

__all__ = [
    # Blueprint
    'notifications_bp',

    # Models
    'Notification',
    'EmailTemplate',
    'ScheduledEmail',
    'EmailAutomation',
    'EmailAutomationLog',

    # Services
    'NotificationService',  # Backward compatible (alias for EmailService)
    'EmailService',
    'BulkEmailRecipientService',

    # Clients
    'GraphAPIClient',
    'SMTPClient',
    'EmailClientFactory',
    'MailerSendClient',
    'SendGridClient',

    # Schemas
    'ScheduledEmailSchema',
    'UpdateScheduledEmailSchema',
    'EmailAutomationSchema',
    'UpdateEmailAutomationSchema',
    'RecipientFilterSchema',

    # Use Cases
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

    # Repositories
    'NotificationRepository',
    'EmailTemplateRepository',
]
