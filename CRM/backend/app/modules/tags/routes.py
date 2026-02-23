"""
Tags module routes (backward compatibility shim).

This file re-exports from the new modular structure for backward compatibility.
New code should import from app.modules.tags.routes instead.
"""
from .routes import (
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
