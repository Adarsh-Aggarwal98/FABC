"""
Update Request Status Use Case
"""
from datetime import datetime
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ServiceRequest, RequestStateHistory
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.services.services.status_resolver import StatusResolver, TransitionResolver


class UpdateRequestStatusUseCase(BaseCommandUseCase):
    """
    Update request status.

    Business Rules:
    - Status must be valid (DB-driven validation)
    - Transition must be allowed for the user's role
    - Sets completed_at when status is final
    - Records state change for analytics
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()

    def execute(self, request_id: str, status: str, updated_by_id: str, user_role: str = None) -> UseCaseResult:
        """
        Update the status of a service request.

        Args:
            request_id: ID of the request to update
            status: New status value
            updated_by_id: ID of the user making the change
            user_role: Role of the user (for transition validation)

        Returns:
            UseCaseResult with updated request
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        company_id = request.user.company_id if request.user else None

        # Dynamic status validation from DB
        valid_keys = StatusResolver.get_valid_keys(company_id, 'request')
        if status not in valid_keys:
            return UseCaseResult.fail(f'Invalid status: {status}', 'INVALID_STATUS')

        # Validate transition if role is provided
        if user_role and request.status != status:
            allowed, requires_note = TransitionResolver.validate_transition(
                company_id, request.status, status, user_role
            )
            if not allowed:
                return UseCaseResult.fail(
                    f'Transition from {request.status} to {status} is not allowed for your role',
                    'TRANSITION_NOT_ALLOWED'
                )

        # Track old status for state history
        old_status = request.status

        # Only record if status actually changed
        if old_status != status:
            request.status = status

            if StatusResolver.is_final_status(company_id, status):
                request.completed_at = datetime.utcnow()

            # Record state change for analytics
            RequestStateHistory.record_state_change(
                request_id=request_id,
                from_state=old_status,
                to_state=status,
                user_id=updated_by_id
            )

        db.session.commit()
        return UseCaseResult.ok({'request': request.to_dict(include_notes=True)})
