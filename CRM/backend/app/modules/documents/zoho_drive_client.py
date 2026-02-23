"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.zoho_drive_client import ZohoDriveClient

The actual client is now in app.modules.documents.services.storage.zoho_drive_client
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.storage.zoho_drive_client import ZohoDriveClient

__all__ = ['ZohoDriveClient']
