"""
Audit module repositories
"""
from typing import List, Optional
from datetime import datetime
from app.common.repository import BaseRepository
from app.modules.audit.models.audit_log import ActivityLog


class ActivityLogRepository(BaseRepository[ActivityLog]):
    model = ActivityLog

    def get_by_entity(self, entity_type: str, entity_id: str, limit: int = 50) -> List[ActivityLog]:
        """Get activity logs for a specific entity"""
        return ActivityLog.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(ActivityLog.created_at.desc()).limit(limit).all()

    def get_by_user(self, user_id: str, limit: int = 50) -> List[ActivityLog]:
        """Get activity logs performed by a specific user"""
        return ActivityLog.query.filter_by(
            performed_by_id=user_id
        ).order_by(ActivityLog.created_at.desc()).limit(limit).all()

    def get_for_entity_user(self, entity_id: str, limit: int = 50) -> List[ActivityLog]:
        """Get activity logs for actions on a user entity"""
        return ActivityLog.query.filter_by(
            entity_type='user',
            entity_id=entity_id
        ).order_by(ActivityLog.created_at.desc()).limit(limit).all()

    def get_by_company(
        self,
        company_id: str,
        entity_type: str = None,
        action: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        page: int = 1,
        per_page: int = 50
    ):
        """Get activity logs for a company with optional filters"""
        query = ActivityLog.query.filter_by(company_id=company_id)

        if entity_type:
            query = query.filter_by(entity_type=entity_type)

        if action:
            query = query.filter_by(action=action)

        if date_from:
            query = query.filter(ActivityLog.created_at >= date_from)

        if date_to:
            query = query.filter(ActivityLog.created_at <= date_to)

        query = query.order_by(ActivityLog.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def search(
        self,
        company_id: str = None,
        entity_type: str = None,
        entity_id: str = None,
        action: str = None,
        performed_by_id: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        page: int = 1,
        per_page: int = 50
    ):
        """Advanced search for activity logs"""
        query = ActivityLog.query

        if company_id:
            query = query.filter_by(company_id=company_id)

        if entity_type:
            query = query.filter_by(entity_type=entity_type)

        if entity_id:
            query = query.filter_by(entity_id=entity_id)

        if action:
            query = query.filter_by(action=action)

        if performed_by_id:
            query = query.filter_by(performed_by_id=performed_by_id)

        if date_from:
            query = query.filter(ActivityLog.created_at >= date_from)

        if date_to:
            query = query.filter(ActivityLog.created_at <= date_to)

        query = query.order_by(ActivityLog.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)
