"""
Update Cost Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class UpdateCostUseCase(BaseCommandUseCase):
    """
    Update cost details for a service request.

    Business Rules:
    - Only admin or accountant can update costs
    - Updates actual_cost, cost_notes, labor_hours, labor_rate
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, user_id: str,
                actual_cost: float = None, cost_notes: str = None,
                labor_hours: float = None, labor_rate: float = None) -> UseCaseResult:
        """
        Update cost details for a service request.

        Args:
            request_id: ID of the request to update
            user_id: ID of the user making the update
            actual_cost: Actual cost incurred
            cost_notes: Notes about the costs
            labor_hours: Hours spent on the job
            labor_rate: Hourly rate used

        Returns:
            UseCaseResult with updated request
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Service request not found', 'NOT_FOUND')

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Check permission
        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Update cost fields
        if actual_cost is not None:
            request.actual_cost = actual_cost
        if cost_notes is not None:
            request.cost_notes = cost_notes
        if labor_hours is not None:
            request.labor_hours = labor_hours
        if labor_rate is not None:
            request.labor_rate = labor_rate

        db.session.commit()

        return UseCaseResult.ok({
            'request': request.to_dict(include_notes=True, include_cost=True)
        })
