"""
RequestStateHistory Repository - Data access for RequestStateHistory entity
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.common.repository import BaseRepository
from app.modules.services.models import RequestStateHistory, ServiceRequest
from app.extensions import db


class StateHistoryRepository(BaseRepository[RequestStateHistory]):
    """Repository for RequestStateHistory data access"""
    model = RequestStateHistory

    def get_by_request(self, request_id: str) -> List[RequestStateHistory]:
        """Get state history for a service request"""
        return RequestStateHistory.query.filter_by(service_request_id=request_id)\
            .order_by(RequestStateHistory.changed_at.asc()).all()

    def get_latest_state(self, request_id: str) -> RequestStateHistory:
        """Get the most recent state history entry for a request"""
        return RequestStateHistory.query.filter_by(service_request_id=request_id)\
            .order_by(RequestStateHistory.changed_at.desc()).first()

    def get_state_durations(self, request_id: str) -> Dict[str, float]:
        """Get duration summary for each state a request has been in"""
        return RequestStateHistory.get_state_durations(request_id)

    def get_average_state_durations(self, company_id: str = None, days: int = 30) -> List[Any]:
        """Get average duration for each state across all requests"""
        return RequestStateHistory.get_average_state_durations(company_id, days)

    def get_transitions_by_user(self, user_id: str, limit: int = 100) -> List[RequestStateHistory]:
        """Get recent state transitions made by a user"""
        return RequestStateHistory.query.filter_by(changed_by_id=user_id)\
            .order_by(RequestStateHistory.changed_at.desc())\
            .limit(limit).all()

    def get_recent_transitions(self, company_id: str = None, limit: int = 100) -> List[RequestStateHistory]:
        """Get recent state transitions, optionally filtered by company"""
        query = RequestStateHistory.query
        if company_id:
            query = query.join(ServiceRequest).filter(
                ServiceRequest.user.has(company_id=company_id)
            )
        return query.order_by(RequestStateHistory.changed_at.desc()).limit(limit).all()

    def get_transitions_to_state(self, to_state: str, days: int = 30) -> List[RequestStateHistory]:
        """Get all transitions to a specific state within a time period"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return RequestStateHistory.query.filter(
            RequestStateHistory.to_state == to_state,
            RequestStateHistory.changed_at >= cutoff
        ).order_by(RequestStateHistory.changed_at.desc()).all()

    def count_by_request(self, request_id: str) -> int:
        """Count state history entries for a service request"""
        return RequestStateHistory.query.filter_by(service_request_id=request_id).count()
