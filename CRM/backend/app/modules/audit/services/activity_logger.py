"""
Activity Logger Service
Handles logging of user activities across the system.
"""
from flask import request, has_request_context
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.modules.audit.models import ActivityLog


class ActivityLogger:
    """Service for logging user activities"""

    @staticmethod
    def log(
        entity_type: str,
        entity_id: str,
        action: str,
        details: dict = None,
        performed_by_id: str = None,
        company_id: str = None
    ) -> ActivityLog:
        """
        Log an activity.

        Args:
            entity_type: Type of entity (user, service_request, etc.)
            entity_id: ID of the affected entity
            action: Action performed (created, updated, etc.)
            details: Additional details as dict
            performed_by_id: ID of user who performed the action (auto-detected if not provided)
            company_id: Company ID for scoping (auto-detected if not provided)
        """
        # Auto-detect performer if not provided
        if performed_by_id is None and has_request_context():
            try:
                performed_by_id = get_jwt_identity()
            except Exception:
                pass

        # Auto-detect company if not provided
        if company_id is None and performed_by_id:
            try:
                from app.modules.user.models import User
                user = User.query.get(performed_by_id)
                if user:
                    company_id = user.company_id
            except Exception:
                pass

        # Get request metadata
        ip_address = None
        user_agent = None
        if has_request_context():
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')[:500]

        log_entry = ActivityLog(
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            details=details,
            performed_by_id=performed_by_id,
            company_id=company_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.session.add(log_entry)
        # Don't commit here - let the calling code manage transactions
        db.session.flush()

        return log_entry

    @staticmethod
    def log_create(entity_type: str, entity_id: str, entity_data: dict = None, **kwargs):
        """Log entity creation"""
        return ActivityLogger.log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=ActivityLog.ACTION_CREATED,
            details={'data': entity_data},
            **kwargs
        )

    @staticmethod
    def log_update(entity_type: str, entity_id: str, changes: dict = None, **kwargs):
        """Log entity update"""
        return ActivityLogger.log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=ActivityLog.ACTION_UPDATED,
            details={'changes': changes},
            **kwargs
        )

    @staticmethod
    def log_delete(entity_type: str, entity_id: str, entity_data: dict = None, **kwargs):
        """Log entity deletion"""
        return ActivityLogger.log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=ActivityLog.ACTION_DELETED,
            details={'data': entity_data},
            **kwargs
        )

    @staticmethod
    def log_status_change(entity_type: str, entity_id: str, old_status: str, new_status: str, **kwargs):
        """Log status change"""
        return ActivityLogger.log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=ActivityLog.ACTION_STATUS_CHANGED,
            details={'old_status': old_status, 'new_status': new_status},
            **kwargs
        )

    @staticmethod
    def log_assignment(entity_type: str, entity_id: str, assignee_id: str, assignee_name: str = None, **kwargs):
        """Log assignment action"""
        return ActivityLogger.log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=ActivityLog.ACTION_ASSIGNED,
            details={'assignee_id': assignee_id, 'assignee_name': assignee_name},
            **kwargs
        )

    @staticmethod
    def log_login(user_id: str, **kwargs):
        """Log user login"""
        return ActivityLogger.log(
            entity_type=ActivityLog.ENTITY_USER,
            entity_id=user_id,
            action=ActivityLog.ACTION_LOGIN,
            performed_by_id=user_id,
            **kwargs
        )

    @staticmethod
    def log_tag_action(user_id: str, tag_id: int, tag_name: str, action: str, **kwargs):
        """Log tag assignment/removal"""
        return ActivityLogger.log(
            entity_type=ActivityLog.ENTITY_USER,
            entity_id=user_id,
            action=action,
            details={'tag_id': tag_id, 'tag_name': tag_name},
            **kwargs
        )
