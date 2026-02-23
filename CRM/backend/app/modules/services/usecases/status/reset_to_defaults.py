"""Reset to system defaults use case."""

from app.extensions import db
from app.common.usecase import UseCaseResult
from app.modules.services.repositories.status_repository import (
    SystemRequestStatusRepository,
    CompanyRequestStatusRepository
)


class ResetToSystemDefaultsUseCase:
    """Reset company statuses to system defaults."""

    def __init__(self):
        self.company_repo = CompanyRequestStatusRepository()

    def execute(self, company_id: str) -> UseCaseResult:
        """Delete all custom statuses, reverting to system defaults."""
        try:
            from app.modules.services.models import ServiceRequest

            # Check if any requests use custom statuses
            custom_statuses = self.company_repo.list_by_company(company_id)
            custom_keys = [s.status_key for s in custom_statuses]

            # Get system status keys to compare
            system_repo = SystemRequestStatusRepository()
            system_statuses = system_repo.get_all_active()
            system_keys = [s.status_key for s in system_statuses]

            # Find custom keys that don't exist in system
            unique_custom_keys = [k for k in custom_keys if k not in system_keys]

            if unique_custom_keys:
                # Check if any requests use these unique statuses
                request_count = ServiceRequest.query.filter(
                    ServiceRequest.status.in_(unique_custom_keys)
                ).join(ServiceRequest.user).filter_by(
                    company_id=company_id
                ).count()

                if request_count > 0:
                    return UseCaseResult.fail(
                        f"Cannot reset - {request_count} requests use custom statuses not in system defaults",
                        'CUSTOM_STATUS_IN_USE'
                    )

            # Delete all custom statuses
            self.company_repo.delete_all_for_company(company_id)
            db.session.commit()

            return UseCaseResult.ok({
                'message': 'Statuses reset to system defaults'
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'RESET_ERROR')
