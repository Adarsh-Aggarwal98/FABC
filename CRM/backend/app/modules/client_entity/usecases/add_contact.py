"""
Add Contact Use Case
=====================
Business logic for adding a contact to a ClientEntity.
"""

from datetime import date
from app.extensions import db
from ..models import ClientEntityContact
from ..repositories import ClientEntityRepository, ClientEntityContactRepository
from .result import UseCaseResult


class AddContactUseCase:
    """Use case for adding a contact to a ClientEntity."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()
        self.contact_repo = ClientEntityContactRepository()

    def execute(
        self,
        entity_id: str,
        company_id: str,
        first_name: str,
        last_name: str,
        email: str = None,
        phone: str = None,
        position: str = None,
        contact_type: str = ClientEntityContact.TYPE_PRIMARY,
        is_primary: bool = False,
        user_id: str = None,
        effective_from: date = None,
        notes: str = None
    ) -> UseCaseResult:
        """Add a contact to a client entity."""
        try:
            # Verify entity exists and belongs to company
            entity = self.entity_repo.get_by_id_and_company(entity_id, company_id)
            if not entity:
                return UseCaseResult.fail('Entity not found', 'NOT_FOUND')

            # If setting as primary, unset existing primary
            if is_primary:
                self.contact_repo.unset_primary_for_entity(entity_id)

            # Create contact
            contact = ClientEntityContact(
                client_entity_id=entity_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                position=position,
                contact_type=contact_type,
                is_primary=is_primary,
                user_id=user_id,
                effective_from=effective_from or date.today(),
                notes=notes
            )

            self.contact_repo.create(contact)
            db.session.commit()

            return UseCaseResult.ok({
                'contact': contact.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'ADD_CONTACT_ERROR')
