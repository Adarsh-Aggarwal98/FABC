"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.sharepoint_client import SharePointClient

The actual client is now in app.modules.documents.services.storage.sharepoint_client
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.storage.sharepoint_client import SharePointClient

__all__ = ['SharePointClient']
