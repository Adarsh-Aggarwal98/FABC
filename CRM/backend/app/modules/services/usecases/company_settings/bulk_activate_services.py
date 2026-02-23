"""
Bulk Activate Services Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import CompanyServiceSettings
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class BulkActivateServicesUseCase(BaseCommandUseCase):
    """Bulk activate or deactivate multiple services for a company."""

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, service_ids: list, user_id: str, is_active: bool) -> UseCaseResult:
        """
        Bulk activate or deactivate services for a company.

        Args:
            service_ids: List of service IDs to update
            user_id: ID of the requesting user
            is_active: Whether to activate or deactivate

        Returns:
            UseCaseResult with count of updated services
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
            return UseCaseResult.fail('Only admins can manage service activation', 'FORBIDDEN')

        company_id = user.company_id
        if not company_id:
            return UseCaseResult.fail('User must belong to a company', 'NO_COMPANY')

        updated_count = 0
        for service_id in service_ids:
            service = self.service_repo.get_by_id(service_id)
            if not service or not service.is_default:
                continue

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

            updated_count += 1

        db.session.commit()

        return UseCaseResult.ok({
            'updated_count': updated_count,
            'message': f"{updated_count} service(s) {'activated' if is_active else 'deactivated'} successfully"
        })
