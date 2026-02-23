"""
Google Drive Integration Module (Backward Compatible)

This module maintains backward compatibility with existing code.
The actual implementation has been moved to the clean architecture structure.

Usage:
    from app.modules.integrations.google_drive import google_drive_bp
    app.register_blueprint(google_drive_bp)
"""

# Import from new clean architecture locations
from ..services.google_drive_service import (
    GoogleDriveConfig,
    GoogleDriveAuthClient,
    GoogleDriveAPIClient
)
from ..routes.google_drive_routes import google_drive_bp, init_google_drive_routes

__all__ = [
    'GoogleDriveConfig',
    'GoogleDriveAuthClient',
    'GoogleDriveAPIClient',
    'google_drive_bp',
    'init_google_drive_routes',
]
