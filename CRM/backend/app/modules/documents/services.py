"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.services import DocumentService

The actual service is now in app.modules.documents.services.document_service
"""
# Re-export from new location for backward compatibility
from app.modules.documents.services.document_service import DocumentService

__all__ = ['DocumentService']
