"""
End Contact Use Case
=====================
Business logic for ending a contact's effective period.
"""

from datetime import date
from app.extensions import db
from ..repositories import ClientEntityRepository, ClientEntityContactRepository
from .result import UseCaseResult


class EndContactUseCase:
    """Use case for ending a contact's effective period."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()
        self.contact_repo = ClientEntityContactRepository()

    def execute(
        self,
        entity_id: str,
        contact_id: int,
        company_id: str,
        end_date: date = None,
        reason: str = None
    ) -> UseCaseResult:
        """End a contact's effective period."""
        try:
            # Verify entity exists and belongs to company
            entity = self.entity_repo.get_by_id_and_company(entity_id, company_id)
            if not entity:
                return UseCaseResult.fail('Entity not found', 'NOT_FOUND')

            # Get contact
            contact = self.contact_repo.get_by_id_and_entity(contact_id, entity_id)
            if not contact:
                return UseCaseResult.fail('Contact not found', 'CONTACT_NOT_FOUND')

            # End the contact
            contact.end_contact(end_date, reason)
            db.session.commit()

            return UseCaseResult.ok({
                'contact': contact.to_dict(),
                'message': 'Contact ended successfully'
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'END_CONTACT_ERROR')
