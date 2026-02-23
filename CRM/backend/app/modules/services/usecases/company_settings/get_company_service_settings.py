"""
Get Company Service Settings Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.models import CompanyServiceSettings
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository


class GetCompanyServiceSettingsUseCase(BaseQueryUseCase):
    """Get company-specific settings for a service"""

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, service_id: int, user_id: str) -> UseCaseResult:
        """
        Get company-specific settings for a service.

        Args:
            service_id: ID of the service
            user_id: ID of the requesting user

        Returns:
            UseCaseResult with service and settings data
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        service = self.service_repo.get_by_id(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        settings = CompanyServiceSettings.query.filter_by(
            company_id=user.company_id,
            service_id=service_id
        ).first()

        service_data = service.to_dict(include_form=True, company_id=user.company_id)

        return UseCaseResult.ok({
            'service': service_data,
            'settings': settings.to_dict() if settings else None
        })
