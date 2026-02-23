"""
Update Request Use Case
"""
from datetime import datetime
from typing import Dict, Any
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ServiceRequest, RequestAuditLog
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class UpdateRequestUseCase(BaseCommandUseCase):
    """
    Update a service request (admin/owner can edit, changes are audited).

    Business Rules:
    - Staff (admin, accountant) or owner can update
    - Different fields are editable based on role
    - All changes are logged in audit log
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, user_id: str, updates: Dict[str, Any],
                is_admin: bool = False) -> UseCaseResult:
        """
        Update a service request with auditing.

        Args:
            request_id: ID of the request to update
            user_id: ID of the user making the update
            updates: Dictionary of fields to update
            is_admin: Whether the user has admin privileges

        Returns:
            UseCaseResult with updated request
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Check access - staff or owner can edit
        is_staff = user.role.name in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]
        is_owner = request.user_id == user_id

        if not is_staff and not is_owner:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        # Practice admins can only edit requests from their company
        if user.role.name == Role.ADMIN:
            if request.user.company_id != user.company_id:
                return UseCaseResult.fail('Cannot edit requests outside your company', 'FORBIDDEN')

        # Determine which fields this user can edit based on role
        allowed_fields = self._get_allowed_fields(user.role.name)

        changes = {}
        for field in allowed_fields:
            if field in updates:
                old_value = getattr(request, field)
                new_value = updates[field]

                # Convert types for comparison
                if field in ['invoice_raised', 'invoice_paid']:
                    new_value = bool(new_value) if new_value is not None else None
                elif field == 'invoice_amount':
                    new_value = float(new_value) if new_value is not None else None
                    old_value = float(old_value) if old_value is not None else None

                if str(old_value) != str(new_value):
                    changes[field] = (old_value, new_value)
                    setattr(request, field, new_value)

        # Log all changes
        if changes:
            RequestAuditLog.log_changes(request_id, user_id, changes)

            # Update completed_at if status changed to completed
            if 'status' in changes and updates.get('status') == 'completed':
                request.completed_at = datetime.utcnow()

            db.session.commit()

        return UseCaseResult.ok({'request': request.to_dict(include_notes=is_staff)})

    def _get_allowed_fields(self, role_name: str) -> list:
        """Get list of fields that can be edited based on role"""
        # Fields that can ONLY be edited by practice owners (admin/super_admin)
        admin_only_fields = [
            'status', 'xero_reference_job_id', 'internal_reference',
            'invoice_raised', 'invoice_paid', 'invoice_amount', 'payment_link',
            'client_entity_id'
        ]

        # Fields that can be edited by accountants and practice owners
        accountant_editable_fields = ['internal_notes']

        if role_name in [Role.SUPER_ADMIN, Role.ADMIN]:
            return admin_only_fields + accountant_editable_fields
        elif role_name == Role.ACCOUNTANT:
            return accountant_editable_fields
        else:
            return []  # Regular users cannot edit
