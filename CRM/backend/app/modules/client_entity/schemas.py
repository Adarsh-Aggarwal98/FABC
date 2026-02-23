"""
ClientEntity Schemas - Backward Compatibility
==============================================
This file re-exports schemas from the new clean architecture structure
for backward compatibility with existing imports.

New imports should use:
    from app.modules.client_entity.schemas import CreateClientEntitySchema, ...

Or:
    from app.modules.client_entity.schemas.client_entity_schemas import CreateClientEntitySchema
"""

from .schemas import (
    ClientEntityContactSchema,
    CreateClientEntityContactSchema,
    UpdateClientEntityContactSchema,
    TrustDetailsSchema,
    AddressSchema,
    ClientEntitySchema,
    CreateClientEntitySchema,
    UpdateClientEntitySchema,
    ClientEntitySearchSchema,
    ClientEntityListSchema,
)

__all__ = [
    'ClientEntityContactSchema',
    'CreateClientEntityContactSchema',
    'UpdateClientEntityContactSchema',
    'TrustDetailsSchema',
    'AddressSchema',
    'ClientEntitySchema',
    'CreateClientEntitySchema',
    'UpdateClientEntitySchema',
    'ClientEntitySearchSchema',
    'ClientEntityListSchema',
]
