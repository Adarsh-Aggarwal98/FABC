"""
Create Multiple Service Requests Use Case
"""
from flask import current_app
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ServiceRequest
from app.modules.services.repositories import ServiceRepository, ServiceRequestRepository
from app.modules.user.models import User, Role


class CreateMultipleRequestsUseCase(BaseCommandUseCase):
    """Create multiple service requests (during onboarding or bulk creation)"""

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.request_repo = ServiceRequestRepository()

    def execute(self, user_id: str, service_ids: list, description: str = None,
                internal_reference: str = None, xero_reference_job_id: str = None,
                client_entity_id: str = None) -> UseCaseResult:
        """
        Create multiple service requests at once.

        Args:
            user_id: ID of the user creating the requests
            service_ids: List of service IDs to create requests for
            description: Optional description (shared for all requests)
            internal_reference: Practice's internal reference number
            xero_reference_job_id: External job/request ID
            client_entity_id: Optional client entity ID

        Returns:
            UseCaseResult with list of created requests
        """
        # Validate client_entity_id if provided
        if client_entity_id:
            from app.modules.client_entity.models import ClientEntity
            entity = ClientEntity.query.get(client_entity_id)
            if not entity:
                return UseCaseResult.fail('Client entity not found', 'NOT_FOUND')
            # Verify entity belongs to same company as user
            user = User.query.get(user_id)
            if user and user.company_id and entity.company_id != user.company_id:
                return UseCaseResult.fail('Client entity does not belong to your company', 'FORBIDDEN')

        requests_created = []

        for service_id in service_ids:
            service = self.service_repo.get_by_id(service_id)
            if service and service.is_active:
                # Generate unique request number for each request
                request_number = ServiceRequest.generate_request_number()

                request = ServiceRequest(
                    user_id=user_id,
                    service_id=service_id,
                    request_number=request_number,
                    description=description,
                    internal_reference=internal_reference,
                    xero_reference_job_id=xero_reference_job_id,
                    client_entity_id=client_entity_id,
                    status=ServiceRequest.STATUS_PENDING
                )
                self.request_repo.create(request)
                requests_created.append(request)

        db.session.commit()

        # Notify admins for each request
        for request in requests_created:
            self._notify_admins(request)

        return UseCaseResult.ok({
            'requests': [r.to_dict() for r in requests_created],
            'count': len(requests_created)
        })

    def _notify_admins(self, request: ServiceRequest):
        """Send notification to admins (same company only)"""
        try:
            from app.modules.notifications.services import NotificationService

            # Get the company_id of the user who created the request
            request_user = User.query.get(request.user_id)
            if not request_user or not request_user.company_id:
                current_app.logger.warning('Cannot notify admins: request user has no company')
                return

            admin_role = Role.query.filter_by(name=Role.ADMIN).first()

            # Only notify admins from the SAME company
            admins = User.query.filter(
                User.role_id == admin_role.id,
                User.company_id == request_user.company_id,
                User.is_active == True
            ).all()

            if admins:
                NotificationService.send_new_request_notification(request, admins)
        except Exception as e:
            current_app.logger.error(f'Failed to notify admins: {str(e)}')
