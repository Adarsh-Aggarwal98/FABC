"""Get statuses for a company use case."""

from app.common.usecase import UseCaseResult
from app.modules.services.repositories.status_repository import (
    SystemRequestStatusRepository,
    CompanyRequestStatusRepository
)


class GetStatusesUseCase:
    """
    Get statuses for a company.
    Returns custom statuses if defined, otherwise system defaults.
    """

    def __init__(self):
        self.system_repo = SystemRequestStatusRepository()
        self.company_repo = CompanyRequestStatusRepository()

    def execute(self, company_id: str, include_inactive: bool = False, category: str = None) -> UseCaseResult:
        """
        Get statuses for a company.

        Args:
            company_id: The company ID
            include_inactive: Include inactive statuses
            category: Optional filter - 'request', 'task', or 'both'
        """
        try:
            from app.modules.services.models.status_models import CompanyRequestStatus, SystemRequestStatus

            # Check if company has custom statuses
            if self.company_repo.has_custom_statuses(company_id):
                query = CompanyRequestStatus.query.filter_by(company_id=company_id)
                if not include_inactive:
                    query = query.filter_by(is_active=True)
                if category:
                    query = query.filter(
                        (CompanyRequestStatus.category == category) |
                        (CompanyRequestStatus.category == 'both')
                    )
                statuses = query.order_by(CompanyRequestStatus.position).all()
                return UseCaseResult.ok({
                    'statuses': [s.to_dict() for s in statuses],
                    'is_customized': True
                })
            else:
                # Return system defaults
                query = SystemRequestStatus.query.filter_by(is_active=True)
                if category:
                    query = query.filter(
                        (SystemRequestStatus.category == category) |
                        (SystemRequestStatus.category == 'both')
                    )
                statuses = query.order_by(SystemRequestStatus.position).all()
                return UseCaseResult.ok({
                    'statuses': [s.to_dict() for s in statuses],
                    'is_customized': False
                })

        except Exception as e:
            return UseCaseResult.fail(str(e), 'GET_STATUSES_ERROR')
