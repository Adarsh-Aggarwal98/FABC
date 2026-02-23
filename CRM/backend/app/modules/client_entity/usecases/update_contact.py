"""
Update Contact Use Case
========================
Business logic for updating a contact.
"""

from app.extensions import db
from ..repositories import ClientEntityRepository, ClientEntityContactRepository
from .result import UseCaseResult


class UpdateContactUseCase:
    """Use case for updating a contact."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()
        self.contact_repo = ClientEntityContactRepository()

    def execute(
        self,
        entity_id: str,
        contact_id: int,
        company_id: str,
        updates: dict
    ) -> UseCaseResult:
        """Update a contact."""
        try:
            # Verify entity exists and belongs to company
            entity = self.entity_repo.get_by_id_and_company(entity_id, company_id)
            if not entity:
                return UseCaseResult.fail('Entity not found', 'NOT_FOUND')

            # Get contact
            contact = self.contact_repo.get_by_id_and_entity(contact_id, entity_id)
            if not contact:
                return UseCaseResult.fail('Contact not found', 'CONTACT_NOT_FOUND')

            # If setting as primary, unset existing primary
            if updates.get('is_primary') and not contact.is_primary:
                self.contact_repo.unset_primary_for_entity(entity_id)

            # Update contact
            self.contact_repo.update(contact, updates)
            db.session.commit()

            return UseCaseResult.ok({
                'contact': contact.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'UPDATE_CONTACT_ERROR')
