"""
Scheduled Email Use Cases - Business logic for email scheduling
"""
from marshmallow import ValidationError

from app.extensions import db
from app.modules.notifications.models.scheduled_email import ScheduledEmail
from app.modules.notifications.models.email_template import EmailTemplate
from app.modules.notifications.schemas.scheduled_email_schemas import (
    ScheduledEmailSchema, UpdateScheduledEmailSchema
)
from app.modules.notifications.usecases.base import UseCaseResult
from app.modules.user.models import User, Role


class CreateScheduledEmailUseCase:
    """Create a new scheduled email"""

    def execute(self, data: dict, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        if not user.company_id:
            return UseCaseResult(False, error='No company associated with user', error_code='FORBIDDEN')

        # Validate input
        schema = ScheduledEmailSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            return UseCaseResult(False, error=str(e.messages), error_code='VALIDATION_ERROR')

        # Validate recipient based on type
        recipient_type = validated_data['recipient_type']
        if recipient_type == 'single':
            if not validated_data.get('recipient_email') and not validated_data.get('recipient_user_id'):
                return UseCaseResult(
                    False,
                    error='recipient_email or recipient_user_id required for single recipient',
                    error_code='VALIDATION_ERROR'
                )
        elif recipient_type == 'filter':
            if not validated_data.get('recipient_filter'):
                return UseCaseResult(
                    False,
                    error='recipient_filter required for filter type',
                    error_code='VALIDATION_ERROR'
                )

        # Validate content
        if not validated_data.get('template_id') and not validated_data.get('body_html'):
            return UseCaseResult(
                False,
                error='Either template_id or body_html is required',
                error_code='VALIDATION_ERROR'
            )

        # Validate template if provided
        if validated_data.get('template_id'):
            template = EmailTemplate.query.get(validated_data['template_id'])
            if not template:
                return UseCaseResult(False, error='Template not found', error_code='NOT_FOUND')
            if template.company_id and template.company_id != user.company_id:
                return UseCaseResult(False, error='Template not accessible', error_code='FORBIDDEN')

        # Calculate recipients count
        recipients_count = 1
        if recipient_type == 'filter':
            recipients_count = self._count_filtered_recipients(
                user.company_id,
                validated_data.get('recipient_filter', {})
            )

        # Create scheduled email
        scheduled_email = ScheduledEmail(
            company_id=user.company_id,
            recipient_type=recipient_type,
            recipient_email=validated_data.get('recipient_email'),
            recipient_user_id=validated_data.get('recipient_user_id'),
            recipient_filter=validated_data.get('recipient_filter'),
            subject=validated_data['subject'],
            body_html=validated_data.get('body_html', ''),
            template_id=validated_data.get('template_id'),
            template_context=validated_data.get('template_context'),
            scheduled_at=validated_data['scheduled_at'],
            timezone=validated_data.get('timezone', 'UTC'),
            recipients_count=recipients_count,
            created_by=user_id
        )

        db.session.add(scheduled_email)
        db.session.commit()

        return UseCaseResult(True, data={'scheduled_email': scheduled_email.to_dict(include_details=True)})

    def _count_filtered_recipients(self, company_id: str, filter_criteria: dict) -> int:
        """Count users matching the filter criteria"""
        query = User.query.filter_by(company_id=company_id, is_active=True)

        if filter_criteria.get('roles'):
            role_ids = Role.query.filter(Role.name.in_(filter_criteria['roles'])).with_entities(Role.id).all()
            role_ids = [r.id for r in role_ids]
            query = query.filter(User.role_id.in_(role_ids))

        return query.count()


class UpdateScheduledEmailUseCase:
    """Update a scheduled email"""

    def execute(self, email_id: int, data: dict, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        scheduled_email = ScheduledEmail.query.get(email_id)
        if not scheduled_email:
            return UseCaseResult(False, error='Scheduled email not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and scheduled_email.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        # Can only update pending emails
        if scheduled_email.status != ScheduledEmail.STATUS_PENDING:
            return UseCaseResult(
                False,
                error='Can only update pending scheduled emails',
                error_code='INVALID_STATUS'
            )

        # Validate input
        schema = UpdateScheduledEmailSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            return UseCaseResult(False, error=str(e.messages), error_code='VALIDATION_ERROR')

        # Update fields
        for key, value in validated_data.items():
            if hasattr(scheduled_email, key):
                setattr(scheduled_email, key, value)

        db.session.commit()

        return UseCaseResult(True, data={'scheduled_email': scheduled_email.to_dict(include_details=True)})


class CancelScheduledEmailUseCase:
    """Cancel a scheduled email"""

    def execute(self, email_id: int, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        scheduled_email = ScheduledEmail.query.get(email_id)
        if not scheduled_email:
            return UseCaseResult(False, error='Scheduled email not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and scheduled_email.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        if not scheduled_email.cancel():
            return UseCaseResult(
                False,
                error='Can only cancel pending scheduled emails',
                error_code='INVALID_STATUS'
            )

        return UseCaseResult(True, data={'message': 'Scheduled email cancelled'})


class ListScheduledEmailsUseCase:
    """List scheduled emails for a company"""

    def execute(self, user_id: str, status: str = None, page: int = 1, per_page: int = 20) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        if not user.company_id and user.role.name != 'super_admin':
            return UseCaseResult(False, error='No company associated with user', error_code='FORBIDDEN')

        query = ScheduledEmail.query

        if user.role.name != 'super_admin':
            query = query.filter_by(company_id=user.company_id)

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(ScheduledEmail.scheduled_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return UseCaseResult(True, data={
            'scheduled_emails': [e.to_dict() for e in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class GetScheduledEmailUseCase:
    """Get a single scheduled email"""

    def execute(self, email_id: int, user_id: str) -> UseCaseResult:
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult(False, error='User not found', error_code='NOT_FOUND')

        scheduled_email = ScheduledEmail.query.get(email_id)
        if not scheduled_email:
            return UseCaseResult(False, error='Scheduled email not found', error_code='NOT_FOUND')

        # Check permission
        if user.role.name != 'super_admin' and scheduled_email.company_id != user.company_id:
            return UseCaseResult(False, error='Access denied', error_code='FORBIDDEN')

        return UseCaseResult(True, data={'scheduled_email': scheduled_email.to_dict(include_details=True)})
