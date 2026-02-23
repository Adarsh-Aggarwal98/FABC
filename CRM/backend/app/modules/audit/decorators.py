"""
Audit module decorators for automatic activity logging
"""
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.modules.audit.services.activity_logger import ActivityLogger


def log_activity(action: str, entity_type: str, get_entity_id=None):
    """
    Decorator to automatically log activities for use case execution.

    Args:
        action: The action being performed (created, updated, etc.)
        entity_type: The type of entity being affected
        get_entity_id: Optional function to extract entity_id from result
                       If not provided, tries to get 'id' from result data

    Usage:
        @log_activity(action='created', entity_type='service_request')
        def execute(self, ...):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)

            # Only log successful operations
            if hasattr(result, 'success') and result.success:
                try:
                    # Try to extract entity_id
                    entity_id = None
                    if get_entity_id:
                        entity_id = get_entity_id(result)
                    elif hasattr(result, 'data') and isinstance(result.data, dict):
                        # Try common patterns
                        for key in ['id', 'user', 'tag', 'request', 'document', 'note']:
                            if key in result.data:
                                val = result.data[key]
                                if isinstance(val, dict) and 'id' in val:
                                    entity_id = val['id']
                                elif isinstance(val, (str, int)):
                                    entity_id = val
                                break

                    if entity_id:
                        ActivityLogger.log(
                            entity_type=entity_type,
                            entity_id=str(entity_id),
                            action=action,
                            details=result.data if hasattr(result, 'data') else None
                        )
                except Exception as e:
                    # Don't let logging failures break the main operation
                    import logging
                    logging.getLogger(__name__).warning(f'Failed to log activity: {e}')

            return result
        return wrapper
    return decorator
