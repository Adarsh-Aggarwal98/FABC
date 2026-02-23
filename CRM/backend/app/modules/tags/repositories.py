"""
Tags module repositories (backward compatibility shim).

This file re-exports from the new modular structure for backward compatibility.
New code should import from app.modules.tags.repositories instead.
"""
from .repositories import TagRepository

__all__ = ['TagRepository']
