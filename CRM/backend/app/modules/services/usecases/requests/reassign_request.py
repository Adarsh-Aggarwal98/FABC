"""
Reassign Request Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import AssignmentHistory
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class ReassignRequestUseCase(BaseCommandUseCase):
    """
    Reassign a request to another accountant.

    Business Rules:
    - Any accountant/admin in the same company can reassign
    - Super admin can reassign any request
    - New assignee must be accountant or admin in same company
    - Reason is required for audit trail
    - Records assignment history with who, when, and why
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, new_accountant_id: str, reassigned_by_id: str,
                reason: str = None) -> UseCaseResult:
        """
        Reassign a request to a different accountant.

        Args:
            request_id: ID of the request to reassign
            new_accountant_id: ID of the new accountant
            reassigned_by_id: ID of the user making the reassignment
            reason: Required reason for reassignment (for audit trail)

        Returns:
            UseCaseResult with updated request
        """
        # Reason is required for audit trail
        if not reason or not reason.strip():
            return UseCaseResult.fail('Reason is required when assigning/reassigning requests', 'VALIDATION_ERROR')

        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        current_user = self.user_repo.get_by_id(reassigned_by_id)
        if not current_user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Check if user has permission
        # Super admin can reassign any request
        # Admin, senior_accountant, and accountant can reassign requests in their company
        is_super_admin = current_user.role.name == Role.SUPER_ADMIN
        is_admin = current_user.role.name == Role.ADMIN
        is_senior_accountant = current_user.role.name == Role.SENIOR_ACCOUNTANT
        is_accountant = current_user.role.name == Role.ACCOUNTANT

        if not is_super_admin and not is_admin and not is_senior_accountant and not is_accountant:
            return UseCaseResult.fail('Only accountants, senior accountants, admins, or super admins can reassign requests', 'FORBIDDEN')

        # For non-super-admin, check that the request belongs to their company
        if not is_super_admin:
            request_user = self.user_repo.get_by_id(request.user_id)
            if request_user and request_user.company_id != current_user.company_id:
                return UseCaseResult.fail('You can only reassign requests within your company', 'FORBIDDEN')

        # Get new accountant
        new_accountant = self.user_repo.get_by_id(new_accountant_id)
        if not new_accountant:
            return UseCaseResult.fail('Accountant not found', 'NOT_FOUND')

        # Check new accountant is valid role and same company
        if new_accountant.role.name not in [Role.ACCOUNTANT, Role.SENIOR_ACCOUNTANT, Role.ADMIN]:
            return UseCaseResult.fail('Can only reassign to accountants, senior accountants, or admins', 'INVALID_ROLE')

        if current_user.role.name != Role.SUPER_ADMIN:
            if new_accountant.company_id != current_user.company_id:
                return UseCaseResult.fail('Can only reassign to staff in your company', 'FORBIDDEN')

        # Record the assignment change
        old_accountant_id = request.assigned_accountant_id
        AssignmentHistory.record_assignment(
            request_id=request_id,
            from_user_id=old_accountant_id,
            to_user_id=new_accountant_id,
            assigned_by_id=reassigned_by_id,
            assignment_type=AssignmentHistory.TYPE_REASSIGNMENT,
            reason=reason
        )

        # Update the assignment
        request.assigned_accountant_id = new_accountant_id

        db.session.commit()

        return UseCaseResult.ok({
            'request': request.to_dict(include_notes=True),
            'message': f'Request reassigned to {new_accountant.full_name}'
        })
