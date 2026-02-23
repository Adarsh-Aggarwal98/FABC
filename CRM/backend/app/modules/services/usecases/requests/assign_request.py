"""
Assign Request Use Case
"""
from flask import current_app
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ServiceRequest, RequestStateHistory, AssignmentHistory
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class AssignRequestUseCase(BaseCommandUseCase):
    """
    Assign a request to an accountant.

    Business Rules:
    - Request must exist
    - Admin/Accountant can only assign requests within their company
    - Super Admin can assign any request
    - Invoice must be raised before assignment
    - Assignee must be an accountant or admin in same company
    - Notifies assignee about assignment
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, accountant_id: str, assigned_by_id: str,
                deadline_date=None, priority: str = None) -> UseCaseResult:
        """
        Assign a request to an accountant.

        Args:
            request_id: ID of the request to assign
            accountant_id: ID of the accountant to assign to
            assigned_by_id: ID of the user making the assignment
            deadline_date: Optional deadline date
            priority: Optional priority level

        Returns:
            UseCaseResult with updated request
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        # Check if user can access this request
        assigned_by = self.user_repo.get_by_id(assigned_by_id)
        if not assigned_by:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not self.request_repo.can_user_access_request(assigned_by, request):
            return UseCaseResult.fail('Access denied to this request', 'FORBIDDEN')

        # Invoice must be raised before assignment
        if not request.invoice_raised:
            return UseCaseResult.fail(
                'Invoice must be raised before assigning to accountant',
                'INVOICE_NOT_RAISED'
            )

        accountant = self.user_repo.get_by_id(accountant_id)
        if not accountant:
            return UseCaseResult.fail('Staff member not found', 'NOT_FOUND')

        # Can assign to accountants, senior accountants, or admins
        if accountant.role.name not in [Role.ACCOUNTANT, Role.SENIOR_ACCOUNTANT, Role.ADMIN]:
            return UseCaseResult.fail('Can only assign to accountants, senior accountants, or admins', 'INVALID_ROLE')

        # Check assignee is in same company (unless super admin is assigning)
        if assigned_by.role.name != Role.SUPER_ADMIN:
            if accountant.company_id != assigned_by.company_id:
                return UseCaseResult.fail('Can only assign to staff in your company', 'FORBIDDEN')

        # Track old status for state history
        old_status = request.status

        # Update assignment
        request.assigned_accountant_id = accountant_id
        request.status = ServiceRequest.STATUS_ASSIGNED

        # Set deadline if provided
        if deadline_date:
            request.deadline_date = deadline_date

        # Set priority if provided
        if priority and priority in ServiceRequest.VALID_PRIORITIES:
            request.priority = priority

        # Record state change for analytics
        RequestStateHistory.record_state_change(
            request_id=request_id,
            from_state=old_status,
            to_state=ServiceRequest.STATUS_ASSIGNED,
            user_id=assigned_by_id,
            notes=f'Assigned to {accountant.full_name}'
        )

        # Record assignment history for audit trail
        AssignmentHistory.record_assignment(
            request_id=request_id,
            from_user_id=None,  # Initial assignment, no previous assignee
            to_user_id=accountant_id,
            assigned_by_id=assigned_by_id,
            assignment_type=AssignmentHistory.TYPE_INITIAL,
            reason='Initial assignment'
        )

        db.session.commit()

        # Notify accountant
        self._notify_accountant(request)

        return UseCaseResult.ok({'request': request.to_dict(include_notes=True)})

    def _notify_accountant(self, request: ServiceRequest):
        """Send assignment notification to accountant"""
        try:
            from app.modules.notifications.services import NotificationService
            NotificationService.send_assignment_notification(request)
        except Exception as e:
            current_app.logger.error(f'Failed to notify accountant: {str(e)}')
