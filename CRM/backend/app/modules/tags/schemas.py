"""
Tags module validation schemas (backward compatibility shim).

This file re-exports from the new modular structure for backward compatibility.
New code should import from app.modules.tags.schemas instead.
"""
from .schemas import CreateTagSchema, UpdateTagSchema, AssignTagSchema

__all__ = ['CreateTagSchema', 'UpdateTagSchema', 'AssignTagSchema']
