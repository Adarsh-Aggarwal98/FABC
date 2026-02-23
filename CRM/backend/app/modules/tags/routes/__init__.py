"""
Tags module routes.

Re-exports route registration for backward compatibility.
"""
from .tag_routes import (
    list_tags,
    create_tag,
    update_tag,
    delete_tag,
    get_user_tags,
    assign_tag_to_user,
    remove_tag_from_user,
)

__all__ = [
    'list_tags',
    'create_tag',
    'update_tag',
    'delete_tag',
    'get_user_tags',
    'assign_tag_to_user',
    'remove_tag_from_user',
]
