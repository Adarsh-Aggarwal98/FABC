"""
ClientEntity Schemas
=====================
Re-export all schemas for backward compatibility.
"""

from .client_entity_contact_schemas import (
    ClientEntityContactSchema,
    CreateClientEntityContactSchema,
    UpdateClientEntityContactSchema,
)
from .client_entity_schemas import (
    TrustDetailsSchema,
    AddressSchema,
    ClientEntitySchema,
    CreateClientEntitySchema,
    UpdateClientEntitySchema,
    ClientEntitySearchSchema,
    ClientEntityListSchema,
)

__all__ = [
    # Contact schemas
    'ClientEntityContactSchema',
    'CreateClientEntityContactSchema',
    'UpdateClientEntityContactSchema',
    # Entity schemas
    'TrustDetailsSchema',
    'AddressSchema',
    'ClientEntitySchema',
    'CreateClientEntitySchema',
    'UpdateClientEntitySchema',
    'ClientEntitySearchSchema',
    'ClientEntityListSchema',
]
