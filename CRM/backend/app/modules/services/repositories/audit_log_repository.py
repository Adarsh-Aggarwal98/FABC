"""
RequestAuditLog Repository - Data access for RequestAuditLog entity
"""
from typing import List
from app.common.repository import BaseRepository
from app.modules.services.models import RequestAuditLog


class AuditLogRepository(BaseRepository[RequestAuditLog]):
    """Repository for RequestAuditLog data access"""
    model = RequestAuditLog

    def get_by_request(self, request_id: str, page: int = 1, per_page: int = 50):
        """Get audit logs for a service request with pagination"""
        return RequestAuditLog.query.filter_by(service_request_id=request_id)\
            .order_by(RequestAuditLog.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

    def get_all_for_request(self, request_id: str) -> List[RequestAuditLog]:
        """Get all audit logs for a service request"""
        return RequestAuditLog.query.filter_by(service_request_id=request_id)\
            .order_by(RequestAuditLog.created_at.desc()).all()

    def get_by_field(self, request_id: str, field_name: str) -> List[RequestAuditLog]:
        """Get audit logs for a specific field on a request"""
        return RequestAuditLog.query.filter_by(
            service_request_id=request_id,
            field_name=field_name
        ).order_by(RequestAuditLog.created_at.desc()).all()

    def get_by_user(self, user_id: str, limit: int = 100) -> List[RequestAuditLog]:
        """Get recent audit logs for changes made by a user"""
        return RequestAuditLog.query.filter_by(modified_by_id=user_id)\
            .order_by(RequestAuditLog.created_at.desc())\
            .limit(limit).all()

    def get_status_changes(self, request_id: str) -> List[RequestAuditLog]:
        """Get only status change audit logs for a request"""
        return RequestAuditLog.query.filter_by(
            service_request_id=request_id,
            field_name='status'
        ).order_by(RequestAuditLog.created_at.desc()).all()

    def count_by_request(self, request_id: str) -> int:
        """Count audit log entries for a service request"""
        return RequestAuditLog.query.filter_by(service_request_id=request_id).count()
