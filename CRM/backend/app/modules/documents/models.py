"""
Backward Compatibility Module
=============================
This file maintains backward compatibility for imports like:
    from app.modules.documents.models import Document

The actual model is now in app.modules.documents.models.document
"""
# Re-export from new location for backward compatibility
from app.modules.documents.models.document import Document

__all__ = ['Document']
