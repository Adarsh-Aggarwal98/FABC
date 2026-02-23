"""
Documents Module
================

This module provides document management functionality with support for
multiple storage backends:
- Google Drive (OAuth or Apps Script)
- SharePoint / OneDrive
- Azure Blob Storage
- Zoho Drive
- Local filesystem (fallback)

Clean Architecture Structure:
- models/       - Database models (Document)
- repositories/ - Data access layer (DocumentRepository)
- services/     - Business logic (DocumentService, storage clients)
- schemas/      - Validation and serialization schemas
- routes/       - HTTP route handlers

Usage:
------
    from app.modules.documents import documents_bp
    from app.modules.documents.services import DocumentService
    from app.modules.documents.models import Document
    from app.modules.documents.repositories import DocumentRepository

Backward Compatibility:
----------------------
Old imports are still supported:
    from app.modules.documents.models import Document
    from app.modules.documents.services import DocumentService
    from app.modules.documents.routes import *  # Route handlers
"""
from flask import Blueprint

# Create Blueprint
documents_bp = Blueprint('documents', __name__)

# Import routes to register them with the blueprint
from app.modules.documents.routes import document_routes

# Backward compatibility exports
# These allow old import paths to continue working

# Models
from app.modules.documents.models import Document

# Services
from app.modules.documents.services import (
    DocumentService,
    BlobStorageClient,
    GoogleDriveClient,
    GoogleAppsScriptClient,
    SharePointClient,
    OneDriveClient,
    ZohoDriveClient
)

# Repositories
from app.modules.documents.repositories import DocumentRepository

# Schemas
from app.modules.documents.schemas import (
    DocumentUploadSchema,
    DocumentResponseSchema,
    DocumentCategorySchema
)

__all__ = [
    # Blueprint
    'documents_bp',

    # Models
    'Document',

    # Services
    'DocumentService',
    'BlobStorageClient',
    'GoogleDriveClient',
    'GoogleAppsScriptClient',
    'SharePointClient',
    'OneDriveClient',
    'ZohoDriveClient',

    # Repositories
    'DocumentRepository',

    # Schemas
    'DocumentUploadSchema',
    'DocumentResponseSchema',
    'DocumentCategorySchema',
]
