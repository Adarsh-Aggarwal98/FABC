"""
Search Models - Entity models for search module

The search module does not define its own database models as it operates
on entities from other modules (users, service requests, documents).

This file is kept for structural consistency with clean architecture pattern.
"""

# No models specific to search module - it searches across other modules' entities
__all__ = []
