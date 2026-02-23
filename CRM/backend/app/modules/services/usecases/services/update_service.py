"""
Update Service Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.repositories import ServiceRepository


class UpdateServiceUseCase(BaseCommandUseCase):
    """Update a service in the catalog"""

    def __init__(self):
        self.service_repo = ServiceRepository()

    def execute(self, service_id: int, data: dict) -> UseCaseResult:
        """
        Update an existing service.

        Args:
            service_id: ID of the service to update
            data: Dictionary of fields to update

        Returns:
            UseCaseResult with updated service
        """
        service = self.service_repo.get_by_id(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        # Fields that can be updated
        updateable_fields = [
            'name', 'description', 'category', 'base_price', 'is_active',
            'form_id', 'workflow_id', 'cost_percentage', 'cost_category',
            'is_recurring', 'renewal_period_months', 'renewal_reminder_days',
            'renewal_due_month', 'renewal_due_day'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(service, field, data[field])

        db.session.commit()
        return UseCaseResult.ok({'service': service.to_dict()})
