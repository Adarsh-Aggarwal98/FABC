"""
Get Dashboard Metrics Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.models import ServiceRequest
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository
from app.modules.user.models import User, Role


class GetDashboardMetricsUseCase(BaseQueryUseCase):
    """
    Get dashboard metrics based on user role.

    Business Rules:
    - Super Admin: Can see all metrics or filter by company_id
    - Admin: Can see metrics for their company only
    - Accountant: Can see metrics for their assigned requests only
    - User: Can see metrics for their own requests only
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str, company_id: str = None) -> UseCaseResult:
        """
        Get dashboard metrics based on user role.

        Args:
            user_id: ID of the requesting user
            company_id: Optional company filter (super admin only)

        Returns:
            UseCaseResult with metrics data
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Get requests based on role and filter
        requests = self._get_requests_for_metrics(user, company_id)

        # Calculate metrics
        total = len(requests)
        pending = sum(1 for r in requests if r.status in [
            ServiceRequest.STATUS_PENDING,
            ServiceRequest.STATUS_INVOICE_RAISED,
            ServiceRequest.STATUS_ASSIGNED
        ])
        processing = sum(1 for r in requests if r.status == ServiceRequest.STATUS_PROCESSING)
        completed = sum(1 for r in requests if r.status == ServiceRequest.STATUS_COMPLETED)
        queries = sum(1 for r in requests if r.status == ServiceRequest.STATUS_QUERY_RAISED)
        under_review = sum(1 for r in requests if r.status == ServiceRequest.STATUS_ACCOUNTANT_REVIEW_PENDING)

        # Invoice metrics
        invoices_raised = sum(1 for r in requests if r.invoice_raised)
        invoices_paid = sum(1 for r in requests if r.invoice_paid)
        total_revenue = sum(r.invoice_amount or 0 for r in requests if r.invoice_paid)
        pending_payments = sum(r.invoice_amount or 0 for r in requests if r.invoice_raised and not r.invoice_paid)

        return UseCaseResult.ok({
            'metrics': {
                'requests': {
                    'total': total,
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'queries': queries,
                    'under_review': under_review
                },
                'invoices': {
                    'raised': invoices_raised,
                    'paid': invoices_paid,
                    'total_revenue': float(total_revenue),
                    'pending_payments': float(pending_payments)
                }
            }
        })

    def _get_requests_for_metrics(self, user: User, company_id: str = None) -> list:
        """Get requests based on user role for metrics calculation (excludes drafts)"""
        if user.role.name == Role.SUPER_ADMIN:
            if company_id:
                query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                    .filter(User.company_id == company_id)
            else:
                query = ServiceRequest.query
        elif user.role.name == Role.ADMIN:
            query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                .filter(User.company_id == user.company_id)
        elif user.role.name == Role.ACCOUNTANT:
            query = ServiceRequest.query.filter_by(assigned_accountant_id=user.id)
        else:
            query = ServiceRequest.query.filter_by(user_id=user.id)

        # Exclude drafts from metrics
        query = query.filter(ServiceRequest.status != ServiceRequest.STATUS_DRAFT)
        return query.all()
