"""
Tags/Labels Module

Allows Practice Owners to create tags and accountants to assign them to clients.

This module follows clean architecture pattern with:
- models/     - Domain entities and database models
- repositories/ - Data access layer
- usecases/   - Business logic layer
- schemas/    - Validation schemas
- routes/     - HTTP controllers (thin layer)

For backward compatibility, all components are re-exported from this module.
"""
from flask import Blueprint

# Create blueprint first (before importing routes)
tags_bp = Blueprint('tags', __name__)

# Import routes to register them with the blueprint
from .routes import tag_routes  # noqa: E402, F401

# Re-export models for backward compatibility
from .models import ClientTag, user_tags  # noqa: E402

# Re-export repositories for backward compatibility
from .repositories import TagRepository  # noqa: E402

# Re-export usecases for backward compatibility
from .usecases import (  # noqa: E402
    ListTagsUseCase,
    CreateTagUseCase,
    UpdateTagUseCase,
    DeleteTagUseCase,
    AssignTagToUserUseCase,
    RemoveTagFromUserUseCase,
    GetUserTagsUseCase,
)

# Re-export schemas for backward compatibility
from .schemas import CreateTagSchema, UpdateTagSchema, AssignTagSchema  # noqa: E402

__all__ = [
    # Blueprint
    'tags_bp',
    # Models
    'ClientTag',
    'user_tags',
    # Repositories
    'TagRepository',
    # Use cases
    'ListTagsUseCase',
    'CreateTagUseCase',
    'UpdateTagUseCase',
    'DeleteTagUseCase',
    'AssignTagToUserUseCase',
    'RemoveTagFromUserUseCase',
    'GetUserTagsUseCase',
    # Schemas
    'CreateTagSchema',
    'UpdateTagSchema',
    'AssignTagSchema',
]
