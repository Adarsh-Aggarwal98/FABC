"""Reorder statuses use case."""

from typing import List
from app.extensions import db
from app.common.usecase import UseCaseResult
from app.modules.services.repositories.status_repository import CompanyRequestStatusRepository


class ReorderStatusesUseCase:
    """Reorder custom statuses for a company."""

    def __init__(self):
        self.company_repo = CompanyRequestStatusRepository()

    def execute(self, company_id: str, status_ids: List[int]) -> UseCaseResult:
        """Reorder statuses by updating positions."""
        try:
            # Validate all IDs belong to this company
            for status_id in status_ids:
                status = self.company_repo.get_by_id_and_company(status_id, company_id)
                if not status:
                    return UseCaseResult.fail(
                        f"Status {status_id} not found or doesn't belong to company",
                        'INVALID_STATUS_ID'
                    )

            # Reorder
            statuses = self.company_repo.reorder(company_id, status_ids)
            db.session.commit()

            return UseCaseResult.ok({
                'statuses': [s.to_dict() for s in statuses]
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'REORDER_ERROR')
