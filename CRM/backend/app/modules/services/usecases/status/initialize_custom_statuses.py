"""Initialize custom statuses use case."""

from app.extensions import db
from app.common.usecase import UseCaseResult
from app.modules.services.models.status_models import CompanyRequestStatus
from app.modules.services.repositories.status_repository import (
    SystemRequestStatusRepository,
    CompanyRequestStatusRepository
)


class InitializeCustomStatusesUseCase:
    """
    Initialize custom statuses for a company by copying system defaults.
    This enables the company to customize their statuses.
    """

    def __init__(self):
        self.system_repo = SystemRequestStatusRepository()
        self.company_repo = CompanyRequestStatusRepository()

    def execute(self, company_id: str) -> UseCaseResult:
        """Copy system statuses to company for customization."""
        try:
            # Check if already customized
            if self.company_repo.has_custom_statuses(company_id):
                return UseCaseResult.fail(
                    'Company already has custom statuses',
                    'ALREADY_CUSTOMIZED'
                )

            # Get system statuses
            system_statuses = self.system_repo.get_all_active()

            # Create company statuses from system defaults
            custom_statuses = []
            for sys_status in system_statuses:
                custom_status = CompanyRequestStatus(
                    company_id=company_id,
                    status_key=sys_status.status_key,
                    display_name=sys_status.display_name,
                    description=sys_status.description,
                    color=sys_status.color,
                    position=sys_status.position,
                    is_final=sys_status.is_final,
                    category=sys_status.category,
                    is_default=sys_status.is_default
                )
                custom_statuses.append(custom_status)

            self.company_repo.create_batch(custom_statuses)
            db.session.commit()

            return UseCaseResult.ok({
                'statuses': [s.to_dict() for s in custom_statuses],
                'message': 'Custom statuses initialized successfully'
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'INIT_STATUSES_ERROR')
