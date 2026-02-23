"""
JobNote Repository - Data access for JobNote entity
"""
from typing import List, Optional
from app.common.repository import BaseRepository
from app.modules.services.models import JobNote


class JobNoteRepository(BaseRepository[JobNote]):
    """Repository for JobNote data access"""
    model = JobNote

    def get_by_request(self, request_id: str, note_type: str = None,
                       page: int = 1, per_page: int = 20):
        """Get job notes for a service request with optional type filter"""
        query = JobNote.query.filter_by(service_request_id=request_id)
        if note_type:
            query = query.filter_by(note_type=note_type)
        query = query.order_by(JobNote.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_all_for_request(self, request_id: str) -> List[JobNote]:
        """Get all job notes for a service request"""
        return JobNote.query.filter_by(service_request_id=request_id)\
            .order_by(JobNote.created_at.desc()).all()

    def get_time_entries(self, request_id: str) -> List[JobNote]:
        """Get time entry notes for a service request"""
        return JobNote.query.filter_by(
            service_request_id=request_id,
            note_type=JobNote.TYPE_TIME_ENTRY
        ).order_by(JobNote.created_at.desc()).all()

    def get_total_time(self, request_id: str) -> int:
        """Get total time spent on a request in minutes"""
        from sqlalchemy import func
        from app.extensions import db

        result = db.session.query(
            func.sum(JobNote.time_spent_minutes)
        ).filter(
            JobNote.service_request_id == request_id
        ).scalar()
        return result or 0

    def get_by_creator(self, user_id: str, limit: int = 50) -> List[JobNote]:
        """Get recent job notes created by a user"""
        return JobNote.query.filter_by(created_by_id=user_id)\
            .order_by(JobNote.created_at.desc())\
            .limit(limit).all()

    def count_by_request(self, request_id: str) -> int:
        """Count job notes for a service request"""
        return JobNote.query.filter_by(service_request_id=request_id).count()
