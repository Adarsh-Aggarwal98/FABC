"""
Documents Services Package
==========================
Contains business logic services for document operations.
"""
from app.modules.documents.services.document_service import DocumentService

# Also export storage clients for convenience
from app.modules.documents.services.storage import (
    BlobStorageClient,
    GoogleDriveClient,
    GoogleAppsScriptClient,
    SharePointClient,
    OneDriveClient,
    ZohoDriveClient
)

__all__ = [
    'DocumentService',
    'BlobStorageClient',
    'GoogleDriveClient',
    'GoogleAppsScriptClient',
    'SharePointClient',
    'OneDriveClient',
    'ZohoDriveClient'
]
