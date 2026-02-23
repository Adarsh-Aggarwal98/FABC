"""
ClientEntity Use Cases - Backward Compatibility
================================================
This file re-exports use cases from the new clean architecture structure
for backward compatibility with existing imports.

New imports should use:
    from app.modules.client_entity.usecases import CreateClientEntityUseCase, ...

Or:
    from app.modules.client_entity.usecases.create_client_entity import CreateClientEntityUseCase
"""

from .usecases import (
    UseCaseResult,
    CreateClientEntityUseCase,
    UpdateClientEntityUseCase,
    DeleteClientEntityUseCase,
    ListClientEntitiesUseCase,
    SearchClientEntitiesUseCase,
    AddContactUseCase,
    UpdateContactUseCase,
    EndContactUseCase,
)

__all__ = [
    'UseCaseResult',
    'CreateClientEntityUseCase',
    'UpdateClientEntityUseCase',
    'DeleteClientEntityUseCase',
    'ListClientEntitiesUseCase',
    'SearchClientEntitiesUseCase',
    'AddContactUseCase',
    'UpdateContactUseCase',
    'EndContactUseCase',
]
