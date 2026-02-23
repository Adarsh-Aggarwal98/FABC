"""
Create Service Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Service
from app.modules.services.repositories import ServiceRepository


class CreateServiceUseCase(BaseCommandUseCase):
    """Create a new service in the catalog"""

    def __init__(self):
        self.service_repo = ServiceRepository()

    def execute(self, name: str, description: str = None, category: str = None,
                base_price: float = None, form_id: int = None,
                workflow_id: str = None, cost_percentage: float = None,
                cost_category: str = None, is_recurring: bool = False,
                renewal_period_months: int = 12) -> UseCaseResult:
        """
        Create a new service.

        Args:
            name: Service name (required)
            description: Service description
            category: Service category
            base_price: Base price for the service
            form_id: Optional custom form ID
            workflow_id: Optional workflow ID
            cost_percentage: Default cost as percentage of price
            cost_category: Cost category for analytics
            is_recurring: Whether this is a recurring service
            renewal_period_months: Renewal period in months

        Returns:
            UseCaseResult with created service
        """
        # Check if service with same name exists
        existing = self.service_repo.find_by_name(name)
        if existing:
            return UseCaseResult.fail(f'Service with name "{name}" already exists', 'DUPLICATE_NAME')

        service = Service(
            name=name,
            description=description,
            category=category,
            base_price=base_price,
            form_id=form_id,
            workflow_id=workflow_id,
            cost_percentage=cost_percentage,
            cost_category=cost_category,
            is_recurring=is_recurring,
            renewal_period_months=renewal_period_months
        )
        self.service_repo.create(service)
        db.session.commit()

        return UseCaseResult.ok({'service': service.to_dict()})
