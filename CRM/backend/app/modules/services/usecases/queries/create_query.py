"""
Create Query Use Case
"""
from flask import current_app
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ServiceRequest, Query
from app.modules.services.repositories import ServiceRequestRepository, QueryRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import User, Role


class CreateQueryUseCase(BaseCommandUseCase):
    """
    Create a query/message on a request.

    Business Rules:
    - Super Admin can access all requests
    - Admin can access requests within their company
    - Assigned accountant can raise queries on their assigned requests
    - Request owner (user) can respond to queries
    - Staff raises query -> STATUS_QUERY_RAISED, notify user
    - User responds -> STATUS_ACCOUNTANT_REVIEW_PENDING (under review)
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.query_repo = QueryRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, sender_id: str, message: str,
                attachment_url: str = None, is_internal: bool = False) -> UseCaseResult:
        """
        Create a query/message on a request.

        Args:
            request_id: ID of the service request
            sender_id: ID of the user sending the message
            message: Message content
            attachment_url: Optional attachment URL
            is_internal: Whether the message is internal (staff-only)

        Returns:
            UseCaseResult with created query
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        sender = self.user_repo.get_by_id(sender_id)
        if not sender:
            return UseCaseResult.fail('Sender not found', 'NOT_FOUND')

        # Check if user can access this request (respects company boundaries for Admin)
        is_request_owner = request.user_id == sender_id
        can_access = self.request_repo.can_user_access_request(sender, request)

        if not can_access and not is_request_owner:
            return UseCaseResult.fail(
                'Not authorized to post query on this request',
                'FORBIDDEN'
            )

        # Determine if sender is staff (for status updates)
        is_admin = sender.role.name in [Role.SUPER_ADMIN, Role.ADMIN]
        is_assigned_accountant = (
            request.assigned_accountant_id == sender_id and
            sender.role.name == Role.ACCOUNTANT
        )
        is_staff = is_admin or is_assigned_accountant

        # Only staff can create internal messages
        if is_internal and not is_staff:
            is_internal = False

        query = Query(
            service_request_id=request_id,
            sender_id=sender_id,
            message=message,
            attachment_url=attachment_url,
            is_internal=is_internal
        )
        self.query_repo.create(query)

        # Update request status based on sender
        if is_staff and not is_internal:
            # Staff raises query -> status = query_raised
            request.status = ServiceRequest.STATUS_QUERY_RAISED
            self._notify_user_query(request, message)
        elif is_request_owner and request.status == ServiceRequest.STATUS_QUERY_RAISED:
            # User responds to query -> status = accountant_review_pending (under review)
            request.status = ServiceRequest.STATUS_ACCOUNTANT_REVIEW_PENDING
            # Notify admin and assigned accountant about user's response
            self._notify_staff_user_response(request, message)

        db.session.commit()
        return UseCaseResult.ok({'query': query.to_dict()})

    def _notify_user_query(self, request: ServiceRequest, message: str):
        """Notify user about new query"""
        try:
            from app.modules.notifications.services import NotificationService
            NotificationService.send_query_notification(request, message)
        except Exception as e:
            current_app.logger.error(f'Failed to send query notification: {str(e)}')

    def _notify_staff_user_response(self, request: ServiceRequest, message: str):
        """Notify admin and assigned accountant when user responds to query"""
        try:
            from app.modules.notifications.services import NotificationService

            # Get the company_id from request user
            request_user = User.query.get(request.user_id)
            if not request_user:
                return

            recipients = []

            # Add assigned accountant if exists
            if request.assigned_accountant_id:
                accountant = User.query.get(request.assigned_accountant_id)
                if accountant and accountant.is_active:
                    recipients.append(accountant)

            # Add admins from the same company
            if request_user.company_id:
                admin_role = Role.query.filter_by(name=Role.ADMIN).first()
                if admin_role:
                    admins = User.query.filter(
                        User.role_id == admin_role.id,
                        User.company_id == request_user.company_id,
                        User.is_active == True
                    ).all()
                    recipients.extend(admins)

            # Remove duplicates (in case accountant is also admin)
            seen_ids = set()
            unique_recipients = []
            for r in recipients:
                if r.id not in seen_ids:
                    seen_ids.add(r.id)
                    unique_recipients.append(r)

            # Send notifications
            NotificationService.send_user_response_notification(request, unique_recipients, message)
        except Exception as e:
            current_app.logger.error(f'Failed to send user response notification: {str(e)}')
