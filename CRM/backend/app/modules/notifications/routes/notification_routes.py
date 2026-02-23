"""
Notification Routes - API Endpoints
===================================

This module provides HTTP endpoints for notification management including:
- In-app notifications (read/unread)
- Email templates (custom per company)
- Bulk email campaigns
- Scheduled emails
- Email automations (trigger-based)

Endpoints:
---------
In-App Notifications:
    GET    /notifications/              - List user notifications
    GET    /notifications/unread-count  - Get unread count
    PATCH  /notifications/<id>/read     - Mark as read
    POST   /notifications/mark-all-read - Mark all as read

Email Templates:
    GET    /notifications/email-templates           - List templates
    POST   /notifications/email-templates           - Create template
    GET    /notifications/email-templates/<id>      - Get template
    PATCH  /notifications/email-templates/<id>      - Update template
    DELETE /notifications/email-templates/<id>      - Delete template
    POST   /notifications/email-templates/<id>/preview - Preview template

Bulk Email:
    POST   /notifications/bulk-email           - Send to user IDs
    GET    /notifications/bulk-email/filters   - Get filter options
    POST   /notifications/bulk-email/preview   - Preview recipients
    POST   /notifications/bulk-email/filtered  - Send to filtered users

Scheduled Emails:
    POST   /notifications/scheduled-emails      - Create scheduled email
    GET    /notifications/scheduled-emails      - List scheduled emails
    GET    /notifications/scheduled-emails/<id> - Get scheduled email
    PATCH  /notifications/scheduled-emails/<id> - Update scheduled email
    POST   /notifications/scheduled-emails/<id>/cancel - Cancel

Email Automations:
    POST   /notifications/automations           - Create automation
    GET    /notifications/automations           - List automations
    GET    /notifications/automations/triggers  - List trigger types
    GET    /notifications/automations/<id>      - Get automation
    PATCH  /notifications/automations/<id>      - Update automation
    DELETE /notifications/automations/<id>      - Delete automation
    POST   /notifications/automations/<id>/toggle - Enable/disable

Author: CRM Development Team
"""

import logging
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError

# Configure module-level logger
logger = logging.getLogger(__name__)

from app.modules.notifications import notifications_bp
from app.modules.notifications.services import EmailService, BulkEmailRecipientService
from app.modules.notifications.services.notification_service import NotificationService
from app.modules.notifications.models import EmailTemplate, ScheduledEmail, EmailAutomation
from app.modules.notifications.usecases import (
    CreateScheduledEmailUseCase, UpdateScheduledEmailUseCase,
    CancelScheduledEmailUseCase, ListScheduledEmailsUseCase, GetScheduledEmailUseCase,
    CreateEmailAutomationUseCase, UpdateEmailAutomationUseCase,
    DeleteEmailAutomationUseCase, ListEmailAutomationsUseCase,
    GetEmailAutomationUseCase, GetAutomationLogsUseCase
)
from app.common.decorators import get_current_user, admin_required, accountant_required
from app.common.responses import success_response, error_response
from app.extensions import db


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for current user"""
    user = get_current_user()
    if not user:
        return error_response('User not found. Please login again.', 401)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'

    pagination = NotificationService.get_user_notifications(
        user.id, unread_only, page, per_page
    )

    return success_response({
        'notifications': [n.to_dict() for n in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications"""
    user = get_current_user()
    if not user:
        return error_response('User not found. Please login again.', 401)

    count = NotificationService.get_unread_count(user.id)
    return success_response({'unread_count': count})


@notifications_bp.route('/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark a notification as read"""
    user = get_current_user()
    if not user:
        return error_response('User not found. Please login again.', 401)

    notification = NotificationService.mark_notification_read(notification_id, user.id)

    if not notification:
        return error_response('Notification not found', 404)

    return success_response({'notification': notification.to_dict()})


@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    """Mark all notifications as read"""
    user = get_current_user()
    if not user:
        return error_response('User not found. Please login again.', 401)

    NotificationService.mark_all_read(user.id)
    return success_response(message='All notifications marked as read')


# ============== Email Template Routes ==============

@notifications_bp.route('/email-templates', methods=['GET'])
@jwt_required()
@accountant_required
def list_email_templates():
    """List email templates available to the user's company"""
    user = get_current_user()

    company_id = user.company_id
    if user.role.name == 'super_admin':
        company_id = request.args.get('company_id')

    templates = EmailTemplate.get_available_templates(company_id)
    return success_response({'templates': [t.to_dict() for t in templates]})


@notifications_bp.route('/email-templates', methods=['POST'])
@jwt_required()
@admin_required
def create_email_template():
    """Create a new email template"""
    import re
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    name = data.get('name')
    slug = data.get('slug')
    subject = data.get('subject')
    # Accept both 'body_html' and 'body' for backward compatibility
    body_html = data.get('body_html') or data.get('body')
    variables = data.get('variables', [])

    if not all([name, subject, body_html]):
        return error_response('name, subject, and body_html (or body) are required', 400)

    # Auto-generate slug from name if not provided
    if not slug:
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # Determine company_id
    company_id = user.company_id
    if user.role.name == 'super_admin':
        company_id = request.json.get('company_id')  # None = system template

    # Check for duplicate slug
    existing = EmailTemplate.query.filter_by(slug=slug, company_id=company_id).first()
    if existing:
        return error_response('A template with this slug already exists', 409)

    template = EmailTemplate(
        name=name,
        slug=slug,
        subject=subject,
        body_html=body_html,
        variables=variables,
        company_id=company_id
    )

    db.session.add(template)
    db.session.commit()

    return success_response({'template': template.to_dict()}, status_code=201)


@notifications_bp.route('/email-templates/<int:template_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_email_template(template_id):
    """Get an email template by ID"""
    template = EmailTemplate.query.get(template_id)

    if not template:
        return error_response('Template not found', 404)

    return success_response({'template': template.to_dict()})


@notifications_bp.route('/email-templates/<int:template_id>', methods=['PATCH', 'PUT'])
@jwt_required()
@admin_required
def update_email_template(template_id):
    """Update an email template"""
    user = get_current_user()
    template = EmailTemplate.query.get(template_id)

    if not template:
        return error_response('Template not found', 404)

    # Check permission
    if user.role.name != 'super_admin' and template.company_id != user.company_id:
        return error_response('Access denied', 403)

    data = request.get_json(silent=True) or {}

    # Update fields
    if 'name' in data:
        template.name = data['name']
    if 'subject' in data:
        template.subject = data['subject']
    # Accept both 'body_html' and 'body' for backward compatibility
    if 'body_html' in data:
        template.body_html = data['body_html']
    elif 'body' in data:
        template.body_html = data['body']
    if 'variables' in data:
        template.variables = data['variables']
    if 'is_active' in data:
        template.is_active = data['is_active']

    db.session.commit()

    return success_response({'template': template.to_dict()})


@notifications_bp.route('/email-templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_email_template(template_id):
    """Delete an email template"""
    user = get_current_user()
    template = EmailTemplate.query.get(template_id)

    if not template:
        return error_response('Template not found', 404)

    # Check permission
    if user.role.name != 'super_admin' and template.company_id != user.company_id:
        return error_response('Access denied', 403)

    # Don't allow deleting system templates unless super admin
    if template.company_id is None and user.role.name != 'super_admin':
        return error_response('Cannot delete system templates', 403)

    db.session.delete(template)
    db.session.commit()

    return success_response({'message': 'Template deleted successfully'})


@notifications_bp.route('/email-templates/<int:template_id>/preview', methods=['POST'])
@jwt_required()
@accountant_required
def preview_email_template(template_id):
    """Preview an email template with sample data"""
    template = EmailTemplate.query.get(template_id)

    if not template:
        return error_response('Template not found', 404)

    context = request.json.get('context', {})
    subject, body = template.render(context)

    return success_response({
        'subject': subject,
        'body_html': body
    })


@notifications_bp.route('/bulk-email', methods=['POST'])
@jwt_required()
@admin_required
def send_bulk_email():
    """Send bulk email to multiple users"""
    user = get_current_user()

    user_ids = request.json.get('user_ids', [])
    template_id = request.json.get('template_id')
    custom_subject = request.json.get('custom_subject')
    custom_body = request.json.get('custom_body')
    context = request.json.get('context', {})

    if not user_ids:
        return error_response('user_ids are required', 400)

    if not template_id and not (custom_subject and custom_body):
        return error_response('Either template_id or custom_subject/custom_body are required', 400)

    # Get template if provided
    template = None
    if template_id:
        template = EmailTemplate.query.get(template_id)
        if not template:
            return error_response('Template not found', 404)

    # Verify all users belong to the sender's company (unless super admin)
    from app.modules.user.models import User, Role

    if user.role.name != 'super_admin':
        invalid_users = User.query.filter(
            User.id.in_(user_ids),
            User.company_id != user.company_id
        ).count()

        if invalid_users > 0:
            return error_response('Some users do not belong to your company', 403)

    # Get recipients
    recipients = User.query.filter(User.id.in_(user_ids)).all()

    if not recipients:
        return error_response('No valid recipients found', 400)

    # Send emails
    sent_count = 0
    failed_count = 0

    for recipient in recipients:
        try:
            # Build context with recipient data
            email_context = {
                **context,
                'client_name': recipient.full_name,
                'client_email': recipient.email
            }

            if template:
                subject, body = template.render(email_context)
            else:
                subject = custom_subject
                body = custom_body
                for key, value in email_context.items():
                    placeholder = f'{{{key}}}'
                    subject = subject.replace(placeholder, str(value) if value else '')
                    body = body.replace(placeholder, str(value) if value else '')

            EmailService.send_email(
                to_email=recipient.email,
                subject=subject,
                body_html=body
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1

    return success_response({
        'sent_count': sent_count,
        'failed_count': failed_count,
        'total_recipients': len(recipients)
    })


# ============== Bulk Email Recipient Filtering Routes ==============

@notifications_bp.route('/bulk-email/filters', methods=['GET'])
@jwt_required()
@admin_required
def get_bulk_email_filter_options():
    """Get available filter options for bulk email"""
    user = get_current_user()

    if not user or not user.company_id:
        return error_response('Company not found', 400)

    summary = BulkEmailRecipientService.get_filter_summary(user.company_id)
    return success_response({'filters': summary})


@notifications_bp.route('/bulk-email/preview', methods=['POST'])
@jwt_required()
@admin_required
def preview_bulk_email_recipients():
    """Preview recipients that match the filter criteria"""
    user = get_current_user()

    if not user or not user.company_id:
        return error_response('Company not found', 400)

    filter_criteria = request.json.get('filter', {})

    # Get count first (more efficient)
    count = BulkEmailRecipientService.count_filtered_recipients(user.company_id, filter_criteria)

    # Only fetch details if count is reasonable
    recipients_preview = []
    if count <= 100:
        recipients = BulkEmailRecipientService.get_filtered_recipients(user.company_id, filter_criteria)
        recipients_preview = [
            {
                'id': r.id,
                'email': r.email,
                'name': r.full_name,
                'role': r.role.name if r.role else None
            }
            for r in recipients
        ]
    else:
        # Just get first 20 as sample
        recipients = BulkEmailRecipientService.get_filtered_recipients(user.company_id, filter_criteria)[:20]
        recipients_preview = [
            {
                'id': r.id,
                'email': r.email,
                'name': r.full_name,
                'role': r.role.name if r.role else None
            }
            for r in recipients
        ]

    return success_response({
        'total_count': count,
        'preview': recipients_preview,
        'showing_sample': count > 100
    })


@notifications_bp.route('/bulk-email/filtered', methods=['POST'])
@jwt_required()
@admin_required
def send_filtered_bulk_email():
    """Send bulk email to filtered recipients"""
    user = get_current_user()

    if not user or not user.company_id:
        return error_response('Company not found', 400)

    filter_criteria = request.json.get('filter', {})
    template_id = request.json.get('template_id')
    custom_subject = request.json.get('custom_subject')
    custom_body = request.json.get('custom_body')
    context = request.json.get('context', {})
    schedule_at = request.json.get('schedule_at')  # Optional: schedule for later

    if not template_id and not (custom_subject and custom_body):
        return error_response('Either template_id or custom_subject/custom_body are required', 400)

    # Get template if provided
    template = None
    if template_id:
        template = EmailTemplate.query.get(template_id)
        if not template:
            return error_response('Template not found', 404)

    # Get filtered recipients
    recipients = BulkEmailRecipientService.get_filtered_recipients(user.company_id, filter_criteria)

    if not recipients:
        return error_response('No recipients match the filter criteria', 400)

    # If scheduling for later, create a scheduled email instead
    if schedule_at:
        from datetime import datetime
        try:
            scheduled_time = datetime.fromisoformat(schedule_at.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return error_response('Invalid schedule_at format. Use ISO 8601.', 400)

        scheduled_email = ScheduledEmail(
            company_id=user.company_id,
            recipient_type=ScheduledEmail.RECIPIENT_FILTER,
            recipient_filter=filter_criteria,
            subject=custom_subject or (template.subject if template else ''),
            body_html=custom_body or (template.body_html if template else ''),
            template_id=template_id,
            template_context=context,
            scheduled_at=scheduled_time,
            recipients_count=len(recipients),
            created_by=user.id
        )
        db.session.add(scheduled_email)
        db.session.commit()

        return success_response({
            'scheduled': True,
            'scheduled_email_id': scheduled_email.id,
            'recipients_count': len(recipients),
            'scheduled_at': schedule_at
        }, status_code=201)

    # Send immediately
    sent_count = 0
    failed_count = 0

    for recipient in recipients:
        try:
            email_context = {
                **context,
                'client_name': recipient.full_name,
                'client_email': recipient.email,
                'first_name': recipient.first_name,
                'last_name': recipient.last_name
            }

            if template:
                subject, body = template.render(email_context)
            else:
                subject = custom_subject
                body = custom_body
                for key, value in email_context.items():
                    placeholder = f'{{{key}}}'
                    subject = subject.replace(placeholder, str(value) if value else '')
                    body = body.replace(placeholder, str(value) if value else '')

            EmailService.send_email(
                to_email=recipient.email,
                subject=subject,
                body_html=body
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1

    return success_response({
        'sent_count': sent_count,
        'failed_count': failed_count,
        'total_recipients': len(recipients)
    })


# ============== Scheduled Email Routes ==============

@notifications_bp.route('/scheduled-emails', methods=['POST'])
@jwt_required()
@admin_required
def create_scheduled_email():
    """Create a new scheduled email"""
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = CreateScheduledEmailUseCase()
    result = usecase.execute(data, user_id)

    if result.success:
        return success_response(result.data, status_code=201)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/scheduled-emails', methods=['GET'])
@jwt_required()
@admin_required
def list_scheduled_emails():
    """List scheduled emails"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')

    usecase = ListScheduledEmailsUseCase()
    result = usecase.execute(user_id, status, page, per_page)

    if result.success:
        return success_response(result.data)
    else:
        return error_response(result.error, 400)


@notifications_bp.route('/scheduled-emails/<int:email_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_scheduled_email(email_id):
    """Get a scheduled email by ID"""
    user_id = get_jwt_identity()

    usecase = GetScheduledEmailUseCase()
    result = usecase.execute(email_id, user_id)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/scheduled-emails/<int:email_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_scheduled_email(email_id):
    """Update a scheduled email"""
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = UpdateScheduledEmailUseCase()
    result = usecase.execute(email_id, data, user_id)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/scheduled-emails/<int:email_id>/cancel', methods=['POST'])
@notifications_bp.route('/scheduled-emails/<int:email_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def cancel_scheduled_email(email_id):
    """Cancel a scheduled email"""
    user_id = get_jwt_identity()

    usecase = CancelScheduledEmailUseCase()
    result = usecase.execute(email_id, user_id)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


# ============== Email Automation Routes ==============

@notifications_bp.route('/automations', methods=['POST'])
@jwt_required()
@admin_required
def create_email_automation():
    """Create a new email automation"""
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = CreateEmailAutomationUseCase()
    result = usecase.execute(data, user_id)

    if result.success:
        return success_response(result.data, status_code=201)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/automations', methods=['GET'])
@jwt_required()
@admin_required
def list_email_automations():
    """List email automations"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    trigger_type = request.args.get('trigger_type')
    active_only = request.args.get('active_only', 'false').lower() == 'true'

    usecase = ListEmailAutomationsUseCase()
    result = usecase.execute(user_id, trigger_type, active_only, page, per_page)

    if result.success:
        return success_response(result.data)
    else:
        return error_response(result.error, 400)


@notifications_bp.route('/automations/triggers', methods=['GET'])
@jwt_required()
@accountant_required
def list_automation_triggers():
    """List available automation triggers"""
    triggers = [
        {'type': 'client_registered', 'name': 'Client Registered', 'description': 'Triggered when a new client signs up'},
        {'type': 'service_requested', 'name': 'Service Requested', 'description': 'Triggered when a service request is created'},
        {'type': 'service_completed', 'name': 'Service Completed', 'description': 'Triggered when a service is marked complete'},
        {'type': 'invoice_sent', 'name': 'Invoice Sent', 'description': 'Triggered when an invoice is sent to a client'},
        {'type': 'invoice_overdue', 'name': 'Invoice Overdue', 'description': 'Triggered when an invoice becomes overdue'},
        {'type': 'payment_received', 'name': 'Payment Received', 'description': 'Triggered when a payment is received'},
        {'type': 'document_uploaded', 'name': 'Document Uploaded', 'description': 'Triggered when a client uploads a document'},
        {'type': 'query_raised', 'name': 'Query Raised', 'description': 'Triggered when a query is raised on a request'},
        {'type': 'birthday', 'name': 'Birthday', 'description': 'Triggered on client birthday'},
        {'type': 'anniversary', 'name': 'Anniversary', 'description': 'Triggered on client company anniversary'},
        {'type': 'inactivity', 'name': 'Inactivity Alert', 'description': 'Triggered when a client has been inactive'},
        {'type': 'custom', 'name': 'Custom Webhook', 'description': 'Triggered via custom webhook'}
    ]
    return success_response({'triggers': triggers})


@notifications_bp.route('/automations/<int:automation_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_email_automation(automation_id):
    """Get an email automation by ID"""
    user_id = get_jwt_identity()

    usecase = GetEmailAutomationUseCase()
    result = usecase.execute(automation_id, user_id)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/automations/<int:automation_id>', methods=['PATCH', 'PUT'])
@jwt_required()
@admin_required
def update_email_automation(automation_id):
    """Update an email automation"""
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = UpdateEmailAutomationUseCase()
    result = usecase.execute(automation_id, data, user_id)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/automations/<int:automation_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_email_automation(automation_id):
    """Delete an email automation"""
    user_id = get_jwt_identity()

    usecase = DeleteEmailAutomationUseCase()
    result = usecase.execute(automation_id, user_id)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/automations/<int:automation_id>/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_automation_logs(automation_id):
    """Get logs for an email automation"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    usecase = GetAutomationLogsUseCase()
    result = usecase.execute(automation_id, user_id, page, per_page)

    if result.success:
        return success_response(result.data)
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return error_response(result.error, status_code)


@notifications_bp.route('/automations/<int:automation_id>/toggle', methods=['POST'])
@jwt_required()
@admin_required
def toggle_automation(automation_id):
    """Toggle an automation on/off"""
    user_id = get_jwt_identity()
    user = get_current_user()

    if not user:
        return error_response('User not found', 401)

    automation = EmailAutomation.query.get(automation_id)
    if not automation:
        return error_response('Automation not found', 404)

    # Check permission
    if user.role.name != 'super_admin' and automation.company_id != user.company_id:
        return error_response('Access denied', 403)

    automation.is_active = not automation.is_active
    db.session.commit()

    return success_response({
        'automation': automation.to_dict(),
        'message': f"Automation {'enabled' if automation.is_active else 'disabled'}"
    })
