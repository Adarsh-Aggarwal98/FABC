"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.blob_storage_client import BlobStorageClient

The actual client is now in app.modules.documents.services.storage.blob_storage_client
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.storage.blob_storage_client import BlobStorageClient

__all__ = ['BlobStorageClient']
