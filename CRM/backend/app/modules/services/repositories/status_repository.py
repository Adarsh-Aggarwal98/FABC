"""
Status Repository
==================
Data access layer for SystemRequestStatus and CompanyRequestStatus.
"""

from typing import Optional, List
from app.extensions import db
from app.modules.services.models.status_models import SystemRequestStatus, CompanyRequestStatus


class SystemRequestStatusRepository:
    """Repository for system-wide status definitions."""

    def get_all_active(self) -> List[SystemRequestStatus]:
        """Get all active system statuses ordered by position."""
        return SystemRequestStatus.query.filter_by(
            is_active=True
        ).order_by(SystemRequestStatus.position).all()

    def get_by_key(self, status_key: str) -> Optional[SystemRequestStatus]:
        """Get a system status by its key."""
        return SystemRequestStatus.query.filter_by(
            status_key=status_key
        ).first()

    def get_by_id(self, status_id: int) -> Optional[SystemRequestStatus]:
        """Get a system status by ID."""
        return SystemRequestStatus.query.get(status_id)


class CompanyRequestStatusRepository:
    """Repository for company-specific status definitions."""

    def get_by_id(self, status_id: int) -> Optional[CompanyRequestStatus]:
        """Get a custom status by ID."""
        return CompanyRequestStatus.query.get(status_id)

    def get_by_id_and_company(self, status_id: int, company_id: str) -> Optional[CompanyRequestStatus]:
        """Get a custom status by ID, ensuring it belongs to the company."""
        return CompanyRequestStatus.query.filter_by(
            id=status_id,
            company_id=company_id
        ).first()

    def get_by_key_and_company(self, status_key: str, company_id: str) -> Optional[CompanyRequestStatus]:
        """Get a custom status by key and company."""
        return CompanyRequestStatus.query.filter_by(
            status_key=status_key,
            company_id=company_id
        ).first()

    def list_by_company(self, company_id: str, include_inactive: bool = False) -> List[CompanyRequestStatus]:
        """List all custom statuses for a company ordered by position."""
        query = CompanyRequestStatus.query.filter_by(company_id=company_id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.order_by(CompanyRequestStatus.position).all()

    def has_custom_statuses(self, company_id: str) -> bool:
        """Check if a company has custom statuses defined."""
        return CompanyRequestStatus.query.filter_by(
            company_id=company_id,
            is_active=True
        ).first() is not None

    def count_by_company(self, company_id: str) -> int:
        """Count active custom statuses for a company."""
        return CompanyRequestStatus.query.filter_by(
            company_id=company_id,
            is_active=True
        ).count()

    def create(self, status: CompanyRequestStatus) -> CompanyRequestStatus:
        """Create a new custom status."""
        db.session.add(status)
        db.session.flush()
        return status

    def create_batch(self, statuses: List[CompanyRequestStatus]) -> List[CompanyRequestStatus]:
        """Create multiple custom statuses at once."""
        db.session.add_all(statuses)
        db.session.flush()
        return statuses

    def update(self, status: CompanyRequestStatus, data: dict) -> CompanyRequestStatus:
        """Update a custom status with the given data."""
        for key, value in data.items():
            if hasattr(status, key) and key not in ('id', 'company_id', 'created_at'):
                setattr(status, key, value)
        db.session.flush()
        return status

    def delete(self, status: CompanyRequestStatus, soft: bool = True) -> None:
        """Delete a custom status (soft delete by default)."""
        if soft:
            status.is_active = False
            db.session.flush()
        else:
            db.session.delete(status)
            db.session.flush()

    def reorder(self, company_id: str, status_ids: List[int]) -> List[CompanyRequestStatus]:
        """Reorder statuses by updating their positions."""
        statuses = []
        for position, status_id in enumerate(status_ids, start=1):
            status = self.get_by_id_and_company(status_id, company_id)
            if status:
                status.position = position
                statuses.append(status)
        db.session.flush()
        return statuses

    def get_next_position(self, company_id: str) -> int:
        """Get the next available position for a new status."""
        max_position = db.session.query(
            db.func.max(CompanyRequestStatus.position)
        ).filter_by(company_id=company_id).scalar()
        return (max_position or 0) + 1

    def delete_all_for_company(self, company_id: str) -> int:
        """Delete all custom statuses for a company (hard delete)."""
        count = CompanyRequestStatus.query.filter_by(
            company_id=company_id
        ).delete()
        db.session.flush()
        return count
