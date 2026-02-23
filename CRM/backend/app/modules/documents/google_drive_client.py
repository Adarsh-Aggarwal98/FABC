"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.google_drive_client import GoogleDriveClient

The actual client is now in app.modules.documents.services.storage.google_drive_client
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.storage.google_drive_client import GoogleDriveClient

__all__ = ['GoogleDriveClient']
