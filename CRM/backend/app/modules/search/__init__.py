"""
Search Module - Global search across entities

This module provides search functionality across multiple entity types
(users, service requests, documents) with advanced filtering.

Architecture:
- models/: Entity models (none specific to search)
- repositories/: Data access layer
- usecases/: Business logic layer
- schemas/: Request/Response validation
- routes/: API endpoint controllers

Backward Compatibility:
- search_bp: Blueprint for routes (unchanged)
- SearchService: Delegates to SearchUseCase (deprecated)
"""
from flask import Blueprint

# Create the main blueprint
search_bp = Blueprint('search', __name__)

# Re-export for backward compatibility
from .services import SearchService

# Import sub-packages for clean access
from . import models
from . import repositories
from . import usecases
from . import schemas
from . import routes as routes_pkg

# Re-export key classes for convenience
from .repositories import SearchRepository
from .usecases import SearchUseCase, get_search_usecase
from .schemas import (
    GlobalSearchRequest,
    UserSearchRequest,
    RequestSearchRequest,
    SearchResult,
    SearchResponse
)

# Import routes to register them with the blueprint
from . import routes  # noqa: E402, F401

__all__ = [
    # Blueprint
    'search_bp',

    # Deprecated (backward compatibility)
    'SearchService',

    # Repository layer
    'SearchRepository',

    # Use case layer
    'SearchUseCase',
    'get_search_usecase',

    # Schemas
    'GlobalSearchRequest',
    'UserSearchRequest',
    'RequestSearchRequest',
    'SearchResult',
    'SearchResponse',

    # Sub-packages
    'models',
    'repositories',
    'usecases',
    'schemas',
    'routes_pkg',
]
