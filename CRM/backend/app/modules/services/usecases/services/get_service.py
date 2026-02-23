"""
Get Service Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.repositories import ServiceRepository


class GetServiceUseCase(BaseQueryUseCase):
    """Get a service by ID"""

    def __init__(self):
        self.service_repo = ServiceRepository()

    def execute(self, service_id: int, include_form: bool = True,
                company_id: str = None) -> UseCaseResult:
        """
        Get a service by ID.

        Args:
            service_id: ID of the service
            include_form: Whether to include form details
            company_id: Optional company ID for company-specific settings

        Returns:
            UseCaseResult with service data
        """
        service = self.service_repo.get_by_id(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        return UseCaseResult.ok({
            'service': service.to_dict(include_form=include_form, company_id=company_id)
        })
