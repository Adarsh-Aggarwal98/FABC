"""
ClientEntity Models - Backward Compatibility
=============================================
This file re-exports models from the new clean architecture structure
for backward compatibility with existing imports.

New imports should use:
    from app.modules.client_entity.models import ClientEntity, ClientEntityContact

Or:
    from app.modules.client_entity.models.client_entity import ClientEntity
    from app.modules.client_entity.models.client_entity_contact import ClientEntityContact
"""

from .models import ClientEntity, ClientEntityContact

__all__ = [
    'ClientEntity',
    'ClientEntityContact',
]
