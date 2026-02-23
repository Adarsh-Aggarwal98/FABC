"""
Tags module use cases.

Re-exports all use cases for backward compatibility.
"""
from .list_tags import ListTagsUseCase
from .create_tag import CreateTagUseCase
from .update_tag import UpdateTagUseCase
from .delete_tag import DeleteTagUseCase
from .assign_tag import AssignTagToUserUseCase
from .remove_tag import RemoveTagFromUserUseCase
from .get_user_tags import GetUserTagsUseCase

__all__ = [
    'ListTagsUseCase',
    'CreateTagUseCase',
    'UpdateTagUseCase',
    'DeleteTagUseCase',
    'AssignTagToUserUseCase',
    'RemoveTagFromUserUseCase',
    'GetUserTagsUseCase',
]
