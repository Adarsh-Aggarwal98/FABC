"""
Query Repository - Data access for Query entity
"""
from typing import List
from app.common.repository import BaseRepository
from app.modules.services.models import Query


class QueryRepository(BaseRepository[Query]):
    """Repository for Query data access"""
    model = Query

    def get_by_request(self, request_id: str, include_internal: bool = True) -> List[Query]:
        """Get all queries for a service request"""
        query = Query.query.filter_by(service_request_id=request_id)
        if not include_internal:
            query = query.filter_by(is_internal=False)
        return query.order_by(Query.created_at.asc()).all()

    def get_external_queries(self, request_id: str) -> List[Query]:
        """Get only external (client-visible) queries for a request"""
        return Query.query.filter_by(
            service_request_id=request_id,
            is_internal=False
        ).order_by(Query.created_at.asc()).all()

    def get_internal_queries(self, request_id: str) -> List[Query]:
        """Get only internal (staff-only) queries for a request"""
        return Query.query.filter_by(
            service_request_id=request_id,
            is_internal=True
        ).order_by(Query.created_at.asc()).all()

    def count_by_request(self, request_id: str) -> int:
        """Count queries for a service request"""
        return Query.query.filter_by(service_request_id=request_id).count()

    def get_unread_count(self, request_id: str, user_id: str) -> int:
        """Get count of queries not sent by the user"""
        return Query.query.filter(
            Query.service_request_id == request_id,
            Query.sender_id != user_id
        ).count()

    def get_by_sender(self, sender_id: str, limit: int = 50) -> List[Query]:
        """Get recent queries sent by a user"""
        return Query.query.filter_by(sender_id=sender_id)\
            .order_by(Query.created_at.desc())\
            .limit(limit).all()
