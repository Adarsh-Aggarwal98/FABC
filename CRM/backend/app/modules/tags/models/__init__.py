"""
Tags module models.

Re-exports all models for backward compatibility.
"""
from .tag import ClientTag, user_tags

__all__ = ['ClientTag', 'user_tags']
