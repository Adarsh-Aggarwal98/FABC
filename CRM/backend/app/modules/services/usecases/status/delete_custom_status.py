"""Delete custom status use case."""

from app.extensions import db
from app.common.usecase import UseCaseResult
from app.modules.services.repositories.status_repository import CompanyRequestStatusRepository


class DeleteCustomStatusUseCase:
    """Delete a custom status (soft delete)."""

    def __init__(self):
        self.company_repo = CompanyRequestStatusRepository()

    def execute(self, status_id: int, company_id: str) -> UseCaseResult:
        """Soft delete a custom status."""
        try:
            from app.modules.services.models import ServiceRequest

            # Get status
            status = self.company_repo.get_by_id_and_company(status_id, company_id)
            if not status:
                return UseCaseResult.fail('Status not found', 'NOT_FOUND')

            # Check if any requests use this status
            request_count = ServiceRequest.query.filter_by(
                status=status.status_key
            ).join(ServiceRequest.user).filter_by(
                company_id=company_id
            ).count()

            if request_count > 0:
                return UseCaseResult.fail(
                    f"Cannot delete status - {request_count} requests use this status",
                    'STATUS_IN_USE'
                )

            # Soft delete
            self.company_repo.delete(status, soft=True)
            db.session.commit()

            return UseCaseResult.ok({
                'message': 'Status deleted successfully'
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'DELETE_STATUS_ERROR')
