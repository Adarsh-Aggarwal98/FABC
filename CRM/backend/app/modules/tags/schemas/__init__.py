"""
Tags module schemas.

Re-exports all schemas for backward compatibility.
"""
from .tag_schemas import CreateTagSchema, UpdateTagSchema, AssignTagSchema

__all__ = ['CreateTagSchema', 'UpdateTagSchema', 'AssignTagSchema']
