"""
Audit/Activity Log module models (Backward Compatibility Shim)

This file is maintained for backward compatibility.
All models have been moved to the models/ subfolder.

Import from:
    from app.modules.audit.models import ActivityLog, ImpersonationSession, AccessLog
or:
    from app.modules.audit import ActivityLog, ImpersonationSession, AccessLog
"""
# Re-export all models from the new location using absolute imports
from app.modules.audit.models.audit_log import ActivityLog, ImpersonationSession
from app.modules.audit.models.access_log import AccessLog

__all__ = [
    'ActivityLog',
    'ImpersonationSession',
    'AccessLog',
]
