"""
Tags/Labels module models (backward compatibility shim).

This file re-exports from the new modular structure for backward compatibility.
New code should import from app.modules.tags.models instead.
"""
from .models import ClientTag, user_tags

__all__ = ['ClientTag', 'user_tags']
