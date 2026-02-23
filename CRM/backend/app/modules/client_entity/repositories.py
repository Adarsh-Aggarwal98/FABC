"""
ClientEntity Repositories - Backward Compatibility
===================================================
This file re-exports repositories from the new clean architecture structure
for backward compatibility with existing imports.

New imports should use:
    from app.modules.client_entity.repositories import ClientEntityRepository, ClientEntityContactRepository

Or:
    from app.modules.client_entity.repositories.client_entity_repository import ClientEntityRepository
    from app.modules.client_entity.repositories.client_entity_contact_repository import ClientEntityContactRepository
"""

from .repositories import ClientEntityRepository, ClientEntityContactRepository

__all__ = [
    'ClientEntityRepository',
    'ClientEntityContactRepository',
]
