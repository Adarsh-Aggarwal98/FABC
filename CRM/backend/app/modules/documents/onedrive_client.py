"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.onedrive_client import OneDriveClient

The actual client is now in app.modules.documents.services.storage.onedrive_client
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.storage.onedrive_client import OneDriveClient

__all__ = ['OneDriveClient']
