"""
List Service Requests Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import Role


class ListServiceRequestsUseCase(BaseQueryUseCase):
    """List service requests based on user role"""

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str, status: str = None,
                page: int = 1, per_page: int = 20,
                company_id: str = None, service_id: int = None,
                invoice_status: str = None, date_from: str = None,
                date_to: str = None, search: str = None,
                accountant_id: str = None, client_user_id: str = None) -> UseCaseResult:
        """
        List service requests with role-based filtering.

        Args:
            user_id: ID of the requesting user
            status: Filter by status
            page: Page number
            per_page: Items per page
            company_id: Filter by company (super admin only)
            service_id: Filter by service type
            invoice_status: Filter by invoice status
            date_from: Filter by start date
            date_to: Filter by end date
            search: Search term for client name or Xero job ID
            accountant_id: Filter by assigned accountant
            client_user_id: Filter by client who created the request

        Returns:
            UseCaseResult with paginated list of requests
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Super Admin can filter by company_id
        filter_company = company_id if user.role.name == Role.SUPER_ADMIN else None

        # Build filters dict
        filters = {
            'service_id': service_id,
            'invoice_status': invoice_status,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
            'accountant_id': accountant_id,
            'user_id': client_user_id  # Filter by client who created the request
        }

        pagination = self.request_repo.get_requests_for_role(
            user, status, page, per_page, company_id=filter_company, **filters
        )
        include_notes = user.role.name in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]

        return UseCaseResult.ok({
            'requests': [r.to_dict(include_notes=include_notes) for r in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
