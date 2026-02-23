"""
Update Company Service Settings Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import CompanyServiceSettings
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class UpdateCompanyServiceSettingsUseCase(BaseCommandUseCase):
    """
    Update company-specific settings for a service (price override, name, etc.).

    Business Rules:
    - Only Admin can update settings for their company
    - Super Admin can manage any company's services
    """

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, service_id: int, user_id: str, data: dict) -> UseCaseResult:
        """
        Update company-specific settings for a service.

        Args:
            service_id: ID of the service
            user_id: ID of the requesting user
            data: Dictionary of settings to update

        Returns:
            UseCaseResult with service and settings data
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
            return UseCaseResult.fail('Only admins can manage service settings', 'FORBIDDEN')

        service = self.service_repo.get_by_id(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        company_id = user.company_id
        if not company_id:
            return UseCaseResult.fail('User must belong to a company', 'NO_COMPANY')

        # Get or create settings
        settings = CompanyServiceSettings.query.filter_by(
            company_id=company_id,
            service_id=service_id
        ).first()

        if not settings:
            settings = CompanyServiceSettings(
                company_id=company_id,
                service_id=service_id
            )
            db.session.add(settings)

        # Update allowed fields
        updateable_fields = [
            'is_active', 'custom_name', 'custom_description',
            'custom_price', 'display_order', 'is_featured'
        ]
        for field in updateable_fields:
            if field in data:
                setattr(settings, field, data[field])

        db.session.commit()

        return UseCaseResult.ok({
            'service': service.to_dict(company_id=company_id),
            'settings': settings.to_dict()
        })
