"""
Service Repository - Data access for Service entity
"""
from typing import Optional, List
from app.common.repository import BaseRepository
from app.modules.services.models import Service


class ServiceRepository(BaseRepository[Service]):
    """Repository for Service data access"""
    model = Service

    def find_by_name(self, name: str) -> Optional[Service]:
        """Find service by name"""
        return Service.query.filter_by(name=name).first()

    def get_active_services(self, category: str = None) -> List[Service]:
        """Get all active services"""
        query = Service.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(Service.name).all()

    def get_all_services(self, active_only: bool = True, category: str = None) -> List[Service]:
        """Get all services with optional filters"""
        query = Service.query
        if active_only:
            query = query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(Service.name).all()

    def get_default_services(self, active_only: bool = True) -> List[Service]:
        """Get all default (system-seeded) services"""
        query = Service.query.filter_by(is_default=True)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Service.name).all()

    def get_recurring_services(self, active_only: bool = True) -> List[Service]:
        """Get all recurring services"""
        query = Service.query.filter_by(is_recurring=True)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Service.name).all()

    def get_by_category(self, category: str, active_only: bool = True) -> List[Service]:
        """Get services by category"""
        query = Service.query.filter_by(category=category)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Service.name).all()

    def get_with_form(self, service_id: int) -> Optional[Service]:
        """Get service with form relationship loaded"""
        return Service.query.options(
            db.joinedload(Service.form)
        ).filter_by(id=service_id).first()
