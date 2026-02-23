"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.google_apps_script_client import GoogleAppsScriptClient

The actual client is now in app.modules.documents.services.storage.google_apps_script_client
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.storage.google_apps_script_client import GoogleAppsScriptClient

__all__ = ['GoogleAppsScriptClient']
