"""
Email Automation Use Cases - Business logic for email automation
"""
from datetime import datetime, timedelta
from marshmallow import ValidationError

from app.extensions import db
from app.modules.notifications.models.email_automation import EmailAutomation, EmailAutomationLog
from app.modules.notifications.models.email_template import EmailTemplate
from app.modules.notifications.models.scheduled_email import ScheduledEmail
from app.modules.notifications.schemas.email_automation_schemas import (
    EmailAutomationSchema, UpdateEmailAutomationSchema
)
from app.modules.notifications.usecases.base import UseCaseResult
from app.modules.user.models import User


class CreateEmailAutomationUseCase:
    """Create a new email automation"""

    def execute(self, data: dict, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        if not user.company_id:
            return UseCaseResult(False, error='No company associated with user', error_code='FORBIDDEN')

        # Validate input
        schema = EmailAutomationSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            return UseCaseResult(False, error=str(e.messages), error_code='VALIDATION_ERROR')

        # Validate template if provided
        if validated_data.get('template_id'):
            template = EmailTemplate.query.get(validated_data['template_id'])
            if not template:
                return UseCaseResult(False, error='Template not found', error_code='NOT_FOUND')
            if template.company_id and template.company_id != user.company_id:
                return UseCaseResult(False, error='Template not accessible', error_code='FORBIDDEN')
        elif not validated_data.get('custom_subject') or not validated_data.get('custom_body'):
            return UseCaseResult(
                False,
                error='Either template_id or custom_subject/custom_body are required',
                error_code='VALIDATION_ERROR'
            )

        # Create automation
        automation = EmailAutomation(
            company_id=user.company_id,
            name=validated_data['name'],
            description=validated_data.get('description'),
            trigger_type=validated_data['trigger_type'],
            trigger_config=validated_data.get('trigger_config'),
            template_id=validated_data.get('template_id'),
            custom_subject=validated_data.get('custom_subject'),
            custom_body=validated_data.get('custom_body'),
            delay_minutes=validated_data.get('delay_minutes', 0),
            conditions=validated_data.get('conditions'),
            is_active=validated_data.get('is_active', True),
            created_by=user_id
        )

        db.session.add(automation)
        db.session.commit()

        return UseCaseResult(True, data={'automation': automation.to_dict(include_template=True)})


class UpdateEmailAutomationUseCase:
    """Update an email automation"""

    def execute(self, automation_id: int, data: dict, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        automation = EmailAutomation.query.get(automation_id)
        if not automation:
            return UseCaseResult(False, error='Automation not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and automation.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        # Validate input
        schema = UpdateEmailAutomationSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            return UseCaseResult(False, error=str(e.messages), error_code='VALIDATION_ERROR')

        # Validate template if being updated
        if validated_data.get('template_id'):
            template = EmailTemplate.query.get(validated_data['template_id'])
            if not template:
                return UseCaseResult(False, error='Template not found', error_code='NOT_FOUND')
            if template.company_id and template.company_id != user.company_id:
                return UseCaseResult(False, error='Template not accessible', error_code='FORBIDDEN')

        # Update fields
        for key, value in validated_data.items():
            if hasattr(automation, key):
                setattr(automation, key, value)

        db.session.commit()

        return UseCaseResult(True, data={'automation': automation.to_dict(include_template=True)})


class DeleteEmailAutomationUseCase:
    """Delete an email automation"""

    def execute(self, automation_id: int, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        automation = EmailAutomation.query.get(automation_id)
        if not automation:
            return UseCaseResult(False, error='Automation not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and automation.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        db.session.delete(automation)
        db.session.commit()

        return UseCaseResult(True, data={'message': 'Automation deleted successfully'})


class ListEmailAutomationsUseCase:
    """List email automations for a company"""

    def execute(
        self, user_id: str, trigger_type: str = None, active_only: bool = False,
        page: int = 1, per_page: int = 20
    ) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        if not user.company_id and user.role.name != 'super_admin':
            return UseCaseResult(False, error='No company associated with user', error_code='FORBIDDEN')

        query = EmailAutomation.query

        if user.role.name != 'super_admin':
            query = query.filter_by(company_id=user.company_id)

        if trigger_type:
            query = query.filter_by(trigger_type=trigger_type)

        if active_only:
            query = query.filter_by(is_active=True)

        query = query.order_by(EmailAutomation.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return UseCaseResult(True, data={
            'automations': [a.to_dict(include_template=True) for a in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class GetEmailAutomationUseCase:
    """Get a single email automation with details"""

    def execute(self, automation_id: int, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        automation = EmailAutomation.query.get(automation_id)
        if not automation:
            return UseCaseResult(False, error='Automation not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and automation.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        return UseCaseResult(True, data={'automation': automation.to_dict(include_template=True)})


class GetAutomationLogsUseCase:
    """Get logs for an email automation"""

    def execute(
        self, automation_id: int, user_id: str, page: int = 1, per_page: int = 20
    ) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        automation = EmailAutomation.query.get(automation_id)
        if not automation:
            return UseCaseResult(False, error='Automation not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and automation.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        pagination = EmailAutomationLog.query.filter_by(
            automation_id=automation_id
        ).order_by(
            EmailAutomationLog.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return UseCaseResult(True, data={
            'logs': [log.to_dict() for log in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class TriggerAutomationUseCase:
    """Trigger automations for a specific event"""

    def execute(
        self, company_id: str, trigger_type: str, recipient_user: User,
        context: dict = None
    ) -> UseCaseResult:
        """
        Trigger all automations matching the trigger type for a company.

        Args:
            company_id: The company ID
            trigger_type: The trigger type (e.g., 'client_registered')
            recipient_user: The user to send the email to
            context: Additional context for template rendering
        """
        from app.modules.notifications.services.email_service import EmailService

        automations = EmailAutomation.get_automations_for_trigger(company_id, trigger_type)

        if not automations:
            return UseCaseResult(True, data={'triggered_count': 0, 'message': 'No automations found'})

        triggered_count = 0
        failed_count = 0

        for automation in automations:
            try:
                # Check conditions if any
                if automation.conditions:
                    if not self._check_conditions(automation.conditions, recipient_user, context):
                        # Log as skipped
                        log = EmailAutomationLog(
                            automation_id=automation.id,
                            recipient_user_id=recipient_user.id,
                            recipient_email=recipient_user.email,
                            trigger_data=context,
                            status=EmailAutomationLog.STATUS_SKIPPED
                        )
                        db.session.add(log)
                        continue

                # Build email content
                email_context = {
                    'client_name': recipient_user.full_name,
                    'client_email': recipient_user.email,
                    'first_name': recipient_user.first_name,
                    'last_name': recipient_user.last_name,
                    **(context or {})
                }

                if automation.template:
                    subject, body = automation.template.render(email_context)
                    if automation.custom_subject:
                        subject = automation.custom_subject
                        for key, value in email_context.items():
                            subject = subject.replace(f'{{{key}}}', str(value) if value else '')
                else:
                    subject = automation.custom_subject or ''
                    body = automation.custom_body or ''
                    for key, value in email_context.items():
                        subject = subject.replace(f'{{{key}}}', str(value) if value else '')
                        body = body.replace(f'{{{key}}}', str(value) if value else '')

                # Handle delay
                if automation.delay_minutes > 0:
                    # Schedule the email instead of sending immediately
                    scheduled = ScheduledEmail(
                        company_id=company_id,
                        recipient_type=ScheduledEmail.RECIPIENT_SINGLE,
                        recipient_user_id=recipient_user.id,
                        recipient_email=recipient_user.email,
                        subject=subject,
                        body_html=body,
                        scheduled_at=datetime.utcnow() + timedelta(minutes=automation.delay_minutes),
                        recipients_count=1
                    )
                    db.session.add(scheduled)

                    log = EmailAutomationLog(
                        automation_id=automation.id,
                        recipient_user_id=recipient_user.id,
                        recipient_email=recipient_user.email,
                        trigger_data=context,
                        status=EmailAutomationLog.STATUS_PENDING
                    )
                else:
                    # Send immediately
                    try:
                        EmailService.send_email(recipient_user.email, subject, body)
                        log = EmailAutomationLog(
                            automation_id=automation.id,
                            recipient_user_id=recipient_user.id,
                            recipient_email=recipient_user.email,
                            trigger_data=context,
                            status=EmailAutomationLog.STATUS_SENT,
                            sent_at=datetime.utcnow()
                        )
                    except Exception as e:
                        log = EmailAutomationLog(
                            automation_id=automation.id,
                            recipient_user_id=recipient_user.id,
                            recipient_email=recipient_user.email,
                            trigger_data=context,
                            status=EmailAutomationLog.STATUS_FAILED,
                            error_message=str(e)
                        )
                        failed_count += 1

                db.session.add(log)
                automation.increment_trigger_count()
                triggered_count += 1

            except Exception as e:
                failed_count += 1

        db.session.commit()

        return UseCaseResult(True, data={
            'triggered_count': triggered_count,
            'failed_count': failed_count
        })

    def _check_conditions(self, conditions: dict, user: User, context: dict) -> bool:
        """Check if conditions are met for the automation"""
        # Check role condition
        if 'roles' in conditions:
            if user.role.name not in conditions['roles']:
                return False

        # Check user status
        if 'user_status' in conditions:
            if not user.is_active and conditions['user_status'] == 'active':
                return False

        # Additional condition checks can be added here
        return True
