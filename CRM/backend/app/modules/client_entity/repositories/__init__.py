"""
ClientEntity Repositories
==========================
Re-export all repositories for backward compatibility.
"""

from .client_entity_repository import ClientEntityRepository
from .client_entity_contact_repository import ClientEntityContactRepository

__all__ = [
    'ClientEntityRepository',
    'ClientEntityContactRepository',
]
