"""
AssignmentHistory Repository - Data access for AssignmentHistory entity
"""
from typing import List
from app.common.repository import BaseRepository
from app.modules.services.models import AssignmentHistory


class AssignmentHistoryRepository(BaseRepository[AssignmentHistory]):
    """Repository for AssignmentHistory data access"""
    model = AssignmentHistory

    def get_by_request(self, request_id: str) -> List[AssignmentHistory]:
        """Get assignment history for a service request"""
        return AssignmentHistory.query.filter_by(service_request_id=request_id)\
            .order_by(AssignmentHistory.created_at.desc()).all()

    def get_by_accountant(self, accountant_id: str, limit: int = 50) -> List[AssignmentHistory]:
        """Get recent assignments to an accountant"""
        return AssignmentHistory.query.filter_by(to_user_id=accountant_id)\
            .order_by(AssignmentHistory.created_at.desc())\
            .limit(limit).all()

    def get_by_assigned_by(self, user_id: str, limit: int = 50) -> List[AssignmentHistory]:
        """Get recent assignments made by a user"""
        return AssignmentHistory.query.filter_by(assigned_by_id=user_id)\
            .order_by(AssignmentHistory.created_at.desc())\
            .limit(limit).all()

    def get_reassignments_count(self, request_id: str) -> int:
        """Get count of reassignments for a request"""
        return AssignmentHistory.query.filter_by(
            service_request_id=request_id,
            assignment_type=AssignmentHistory.TYPE_REASSIGNMENT
        ).count()

    def get_initial_assignment(self, request_id: str) -> AssignmentHistory:
        """Get the initial assignment for a request"""
        return AssignmentHistory.query.filter_by(
            service_request_id=request_id,
            assignment_type=AssignmentHistory.TYPE_INITIAL
        ).first()
