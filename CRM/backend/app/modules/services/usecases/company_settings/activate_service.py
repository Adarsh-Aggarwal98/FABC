"""
Activate Service for Company Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import CompanyServiceSettings
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class ActivateServiceForCompanyUseCase(BaseCommandUseCase):
    """
    Activate or deactivate a default service for a company.

    Business Rules:
    - Only Admin can activate/deactivate services for their company
    - Super Admin can manage any company's services
    - Creates CompanyServiceSettings if not exists
    """

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, service_id: int, user_id: str, is_active: bool) -> UseCaseResult:
        """
        Activate or deactivate a service for a company.

        Args:
            service_id: ID of the service
            user_id: ID of the requesting user
            is_active: Whether to activate or deactivate

        Returns:
            UseCaseResult with service and settings data
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
            return UseCaseResult.fail('Only admins can manage service activation', 'FORBIDDEN')

        service = self.service_repo.get_by_id(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        if not service.is_default:
            return UseCaseResult.fail('Only default services can be activated/deactivated', 'INVALID_SERVICE')

        company_id = user.company_id
        if not company_id:
            return UseCaseResult.fail('User must belong to a company', 'NO_COMPANY')

        # Get or create settings
        settings = CompanyServiceSettings.query.filter_by(
            company_id=company_id,
            service_id=service_id
        ).first()

        if settings:
            settings.is_active = is_active
        else:
            settings = CompanyServiceSettings(
                company_id=company_id,
                service_id=service_id,
                is_active=is_active
            )
            db.session.add(settings)

        db.session.commit()

        return UseCaseResult.ok({
            'service': service.to_dict(company_id=company_id),
            'settings': settings.to_dict(),
            'message': f"Service {'activated' if is_active else 'deactivated'} successfully"
        })
