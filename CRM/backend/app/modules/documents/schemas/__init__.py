"""
Documents Schemas Package
=========================
Contains validation and serialization schemas for documents.
"""
from app.modules.documents.schemas.document_schemas import (
    DocumentUploadSchema,
    DocumentResponseSchema,
    DocumentCategorySchema,
    DocumentListSchema,
    SharingLinkResponseSchema,
    DownloadUrlResponseSchema
)

__all__ = [
    'DocumentUploadSchema',
    'DocumentResponseSchema',
    'DocumentCategorySchema',
    'DocumentListSchema',
    'SharingLinkResponseSchema',
    'DownloadUrlResponseSchema'
]
