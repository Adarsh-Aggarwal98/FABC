"""
Add Internal Note Use Case
"""
from datetime import datetime
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class AddInternalNoteUseCase(BaseCommandUseCase):
    """
    Add internal note to a request.

    Business Rules:
    - Super Admin can add notes to any request
    - Admin can add notes to requests within their company
    - Accountant can add notes to their assigned requests
    - Notes are timestamped with author
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, note: str, added_by_id: str) -> UseCaseResult:
        """
        Add an internal note to a service request.

        Args:
            request_id: ID of the request
            note: Note content
            added_by_id: ID of the user adding the note

        Returns:
            UseCaseResult with updated request
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        added_by = self.user_repo.get_by_id(added_by_id)
        if not added_by:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if added_by.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
            return UseCaseResult.fail('Not authorized to add notes', 'FORBIDDEN')

        # Check company/assignment access
        if not self.request_repo.can_user_access_request(added_by, request):
            return UseCaseResult.fail('Access denied to this request', 'FORBIDDEN')

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        new_note = f"\n[{timestamp}] {added_by.full_name}: {note}"

        if request.internal_notes:
            request.internal_notes += new_note
        else:
            request.internal_notes = new_note.strip()

        db.session.commit()
        return UseCaseResult.ok({'request': request.to_dict(include_notes=True)})
