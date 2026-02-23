"""
Delete Client Entity Use Case
==============================
Business logic for deleting (soft) a ClientEntity.
"""

from app.extensions import db
from ..repositories import ClientEntityRepository
from .result import UseCaseResult


class DeleteClientEntityUseCase:
    """Use case for deleting (soft) a ClientEntity."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()

    def execute(self, entity_id: str, company_id: str) -> UseCaseResult:
        """Soft delete a client entity."""
        try:
            entity = self.entity_repo.get_by_id_and_company(entity_id, company_id)
            if not entity:
                return UseCaseResult.fail('Entity not found', 'NOT_FOUND')

            self.entity_repo.delete(entity, soft=True)
            db.session.commit()

            return UseCaseResult.ok({'message': 'Entity deactivated successfully'})

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'DELETE_ERROR')
