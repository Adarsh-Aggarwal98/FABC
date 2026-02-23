"""
Get Service Request Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.repositories import ServiceRequestRepository


class GetServiceRequestUseCase(BaseQueryUseCase):
    """Get a service request by ID"""

    def __init__(self):
        self.request_repo = ServiceRequestRepository()

    def execute(self, request_id: str, include_notes: bool = False,
                include_cost: bool = False) -> UseCaseResult:
        """
        Get a service request by ID.

        Args:
            request_id: ID of the service request
            include_notes: Whether to include internal notes
            include_cost: Whether to include cost information

        Returns:
            UseCaseResult with request data
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        return UseCaseResult.ok({
            'request': request.to_dict(include_notes=include_notes, include_cost=include_cost)
        })
