"""
Service Repository for Import Operations

Provides data access methods for service-related import operations.
"""
import logging
from typing import Optional, Dict
from datetime import datetime

from app.extensions import db
from app.modules.services.models import Service, ServiceRequest

logger = logging.getLogger(__name__)


class ServiceImportRepository:
    """Repository for service import operations."""

    @staticmethod
    def get_active_services() -> Dict[str, Service]:
        """Get all active services, indexed by lowercase name."""
        services = Service.query.filter_by(is_active=True).all()
        return {service.name.lower(): service for service in services}

    @staticmethod
    def get_all_services() -> Dict[str, Service]:
        """Get all services, indexed by lowercase name."""
        services = Service.query.all()
        return {service.name.lower(): service for service in services}

    @staticmethod
    def get_service_by_name(name: str) -> Optional[Service]:
        """Get a service by name (case-insensitive)."""
        return Service.query.filter(
            db.func.lower(Service.name) == name.lower()
        ).first()

    @staticmethod
    def create_service(
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        base_price: Optional[float] = None,
        is_recurring: bool = False,
        renewal_period_months: int = 12,
        cost_percentage: float = 0
    ) -> Service:
        """
        Create a new service.

        Args:
            name: Service name
            description: Service description
            category: Service category
            base_price: Base price for the service
            is_recurring: Whether the service is recurring
            renewal_period_months: Months between renewals
            cost_percentage: Cost percentage

        Returns:
            The created Service object
        """
        service = Service(
            name=name,
            description=description,
            category=category,
            base_price=base_price,
            is_recurring=is_recurring,
            renewal_period_months=renewal_period_months,
            cost_percentage=cost_percentage,
            is_active=True,
            is_default=False
        )
        db.session.add(service)
        db.session.flush()
        return service

    @staticmethod
    def update_service(
        service: Service,
        description: Optional[str] = None,
        category: Optional[str] = None,
        base_price: Optional[float] = None,
        is_recurring: bool = False,
        renewal_period_months: int = 12,
        cost_percentage: float = 0
    ) -> Service:
        """
        Update an existing service.

        Args:
            service: The service to update
            **kwargs: Fields to update

        Returns:
            The updated Service object
        """
        if description is not None:
            service.description = description or service.description
        if category is not None:
            service.category = category or service.category
        if base_price is not None:
            service.base_price = base_price
        service.is_recurring = is_recurring
        service.renewal_period_months = renewal_period_months
        service.cost_percentage = cost_percentage
        return service

    @staticmethod
    def create_service_request(
        user_id: int,
        service_id: int,
        description: Optional[str] = None,
        status: str = 'pending',
        priority: str = 'normal',
        deadline_date=None,
        invoice_amount: Optional[float] = None,
        invoice_raised: bool = False,
        invoice_paid: bool = False,
        internal_reference: Optional[str] = None,
        internal_notes: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> ServiceRequest:
        """
        Create a new service request.

        Args:
            user_id: ID of the user/client
            service_id: ID of the service
            **kwargs: Optional service request attributes

        Returns:
            The created ServiceRequest object
        """
        service_request = ServiceRequest(
            user_id=user_id,
            service_id=service_id,
            request_number=ServiceRequest.generate_request_number(),
            description=description,
            status=status,
            priority=priority,
            deadline_date=deadline_date,
            invoice_amount=invoice_amount,
            invoice_raised=invoice_raised,
            invoice_paid=invoice_paid,
            internal_reference=internal_reference,
            internal_notes=internal_notes,
            created_at=created_at or datetime.utcnow()
        )

        if status == 'completed':
            service_request.completed_at = datetime.utcnow()

        db.session.add(service_request)
        db.session.flush()
        return service_request

    @staticmethod
    def commit():
        """Commit the current transaction."""
        db.session.commit()
