"""
ClientEntity Use Cases
=======================
Re-export all use cases for backward compatibility.
"""

from .result import UseCaseResult
from .create_client_entity import CreateClientEntityUseCase
from .update_client_entity import UpdateClientEntityUseCase
from .delete_client_entity import DeleteClientEntityUseCase
from .list_client_entities import ListClientEntitiesUseCase
from .search_client_entities import SearchClientEntitiesUseCase
from .add_contact import AddContactUseCase
from .update_contact import UpdateContactUseCase
from .end_contact import EndContactUseCase

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
