"""Get status for request use case."""

from app.common.usecase import UseCaseResult
from app.modules.services.repositories.status_repository import (
    SystemRequestStatusRepository,
    CompanyRequestStatusRepository
)


class GetStatusForRequestUseCase:
    """Get the status configuration for a specific status key."""

    def __init__(self):
        self.system_repo = SystemRequestStatusRepository()
        self.company_repo = CompanyRequestStatusRepository()

    def execute(self, company_id: str, status_key: str) -> UseCaseResult:
        """Get status details for a status key."""
        try:
            # Try company custom status first
            status = self.company_repo.get_by_key_and_company(status_key, company_id)
            if status:
                return UseCaseResult.ok({
                    'status': status.to_dict()
                })

            # Fall back to system status
            status = self.system_repo.get_by_key(status_key)
            if status:
                return UseCaseResult.ok({
                    'status': status.to_dict()
                })

            return UseCaseResult.fail('Status not found', 'NOT_FOUND')

        except Exception as e:
            return UseCaseResult.fail(str(e), 'GET_STATUS_ERROR')
