"""
Update Client Entity Use Case
==============================
Business logic for updating a ClientEntity.
"""

from app.extensions import db
from ..repositories import ClientEntityRepository
from .result import UseCaseResult


class UpdateClientEntityUseCase:
    """Use case for updating a ClientEntity."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()

    def execute(
        self,
        entity_id: str,
        company_id: str,
        updates: dict
    ) -> UseCaseResult:
        """Update a client entity."""
        try:
            # Get entity
            entity = self.entity_repo.get_by_id_and_company(entity_id, company_id)
            if not entity:
                return UseCaseResult.fail('Entity not found', 'NOT_FOUND')

            # Check for duplicate name if name is being updated
            if 'name' in updates and updates['name'] != entity.name:
                existing = self.entity_repo.get_by_name_and_company(
                    updates['name'], company_id
                )
                if existing and existing.id != entity_id:
                    return UseCaseResult.fail(
                        f"An entity with name '{updates['name']}' already exists",
                        'DUPLICATE_NAME'
                    )

            # Update entity
            self.entity_repo.update(entity, updates)
            db.session.commit()

            return UseCaseResult.ok({
                'entity': entity.to_dict(include_primary_contact=True)
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'UPDATE_ERROR')
