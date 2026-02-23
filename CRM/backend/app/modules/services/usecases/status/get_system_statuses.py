"""Get system default statuses use case."""

from app.common.usecase import UseCaseResult
from app.modules.services.repositories.status_repository import SystemRequestStatusRepository


class GetSystemStatusesUseCase:
    """Get system default statuses."""

    def __init__(self):
        self.system_repo = SystemRequestStatusRepository()

    def execute(self) -> UseCaseResult:
        """Get all system default statuses."""
        try:
            statuses = self.system_repo.get_all_active()
            return UseCaseResult.ok({
                'statuses': [s.to_dict() for s in statuses]
            })
        except Exception as e:
            return UseCaseResult.fail(str(e), 'GET_SYSTEM_STATUSES_ERROR')
