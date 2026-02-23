"""
ClientEntity Models
====================
Re-export all models for backward compatibility.
"""

from .client_entity import ClientEntity
from .client_entity_contact import ClientEntityContact

__all__ = [
    'ClientEntity',
    'ClientEntityContact',
]
