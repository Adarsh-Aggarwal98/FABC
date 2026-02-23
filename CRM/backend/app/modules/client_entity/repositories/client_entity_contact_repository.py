"""
ClientEntityContact Repository
===============================
Data access layer for ClientEntityContact.
"""

from typing import Optional, List
from app.extensions import db
from ..models import ClientEntityContact


class ClientEntityContactRepository:
    """Repository for ClientEntityContact data access."""

    def get_by_id(self, contact_id: int) -> Optional[ClientEntityContact]:
        """Get contact by ID."""
        return ClientEntityContact.query.get(contact_id)

    def get_by_id_and_entity(self, contact_id: int, entity_id: str) -> Optional[ClientEntityContact]:
        """Get contact by ID, ensuring it belongs to the entity."""
        return ClientEntityContact.query.filter_by(
            id=contact_id,
            client_entity_id=entity_id
        ).first()

    def list_by_entity(
        self,
        entity_id: str,
        include_inactive: bool = False,
        include_ended: bool = False
    ) -> List[ClientEntityContact]:
        """List contacts for an entity."""
        query = ClientEntityContact.query.filter_by(client_entity_id=entity_id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        if not include_ended:
            query = query.filter(ClientEntityContact.effective_to.is_(None))

        return query.order_by(
            ClientEntityContact.is_primary.desc(),
            ClientEntityContact.effective_from.desc()
        ).all()

    def list_by_entity_with_history(self, entity_id: str) -> List[ClientEntityContact]:
        """List all contacts for an entity, including history."""
        return ClientEntityContact.query.filter_by(
            client_entity_id=entity_id
        ).order_by(
            ClientEntityContact.effective_from.desc()
        ).all()

    def get_primary_contact(self, entity_id: str) -> Optional[ClientEntityContact]:
        """Get the current primary contact for an entity."""
        return ClientEntityContact.query.filter_by(
            client_entity_id=entity_id,
            is_primary=True,
            is_active=True
        ).filter(
            ClientEntityContact.effective_to.is_(None)
        ).first()

    def create(self, contact: ClientEntityContact) -> ClientEntityContact:
        """Create a new contact."""
        db.session.add(contact)
        db.session.flush()
        return contact

    def update(self, contact: ClientEntityContact, data: dict) -> ClientEntityContact:
        """Update a contact with the given data."""
        for key, value in data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        db.session.flush()
        return contact

    def delete(self, contact: ClientEntityContact) -> None:
        """Delete a contact."""
        db.session.delete(contact)
        db.session.flush()

    def unset_primary_for_entity(self, entity_id: str) -> None:
        """Unset primary flag for all contacts of an entity."""
        ClientEntityContact.query.filter_by(
            client_entity_id=entity_id,
            is_primary=True
        ).update({'is_primary': False})
        db.session.flush()

    def get_by_user_and_entity(self, user_id: str, entity_id: str) -> Optional[ClientEntityContact]:
        """Get contact by user and entity (for duplicate checking)."""
        return ClientEntityContact.query.filter_by(
            user_id=user_id,
            client_entity_id=entity_id,
            is_active=True
        ).filter(
            ClientEntityContact.effective_to.is_(None)
        ).first()
