"""Update custom status use case."""

from app.extensions import db
from app.common.usecase import UseCaseResult
from app.modules.services.models.status_models import CompanyRequestStatus
from app.modules.services.repositories.status_repository import CompanyRequestStatusRepository


class UpdateCustomStatusUseCase:
    """Update an existing custom status."""

    def __init__(self):
        self.company_repo = CompanyRequestStatusRepository()

    def execute(
        self,
        status_id: int,
        company_id: str,
        updates: dict
    ) -> UseCaseResult:
        """Update a custom status."""
        try:
            # Get status
            status = self.company_repo.get_by_id_and_company(status_id, company_id)
            if not status:
                return UseCaseResult.fail('Status not found', 'NOT_FOUND')

            # Don't allow changing status_key (it's used in service_requests.status)
            if 'status_key' in updates:
                del updates['status_key']

            # If setting as default, unset other defaults in same category
            if updates.get('is_default'):
                category = updates.get('category', status.category)
                existing_defaults = CompanyRequestStatus.query.filter_by(
                    company_id=company_id,
                    is_default=True
                ).filter(
                    CompanyRequestStatus.id != status_id
                ).filter(
                    (CompanyRequestStatus.category == category) |
                    (CompanyRequestStatus.category == 'both')
                ).all()
                for d in existing_defaults:
                    d.is_default = False

            # Update status
            self.company_repo.update(status, updates)
            db.session.commit()

            return UseCaseResult.ok({
                'status': status.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'UPDATE_STATUS_ERROR')
