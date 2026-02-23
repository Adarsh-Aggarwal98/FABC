"""
Tags module use cases (backward compatibility shim).

This file re-exports from the new modular structure for backward compatibility.
New code should import from app.modules.tags.usecases instead.
"""
from .usecases import (
    ListTagsUseCase,
    CreateTagUseCase,
    UpdateTagUseCase,
    DeleteTagUseCase,
    AssignTagToUserUseCase,
    RemoveTagFromUserUseCase,
    GetUserTagsUseCase,
)

__all__ = [
    'ListTagsUseCase',
    'CreateTagUseCase',
    'UpdateTagUseCase',
    'DeleteTagUseCase',
    'AssignTagToUserUseCase',
    'RemoveTagFromUserUseCase',
    'GetUserTagsUseCase',
]
