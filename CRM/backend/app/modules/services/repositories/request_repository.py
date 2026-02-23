"""
ServiceRequest Repository - Data access for ServiceRequest entity
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import or_
from app.common.repository import BaseRepository
from app.modules.services.models import ServiceRequest
from app.modules.user.models import User, Role


class ServiceRequestRepository(BaseRepository[ServiceRequest]):
    """Repository for ServiceRequest data access"""
    model = ServiceRequest

    def get_by_request_number(self, request_number: str) -> Optional[ServiceRequest]:
        """Get request by unique request number"""
        return ServiceRequest.query.filter_by(request_number=request_number).first()

    def get_by_user(self, user_id: str, status: str = None,
                    page: int = 1, per_page: int = 20):
        """Get requests by user (client view)"""
        query = ServiceRequest.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_by_accountant(self, accountant_id: str, status: str = None,
                          page: int = 1, per_page: int = 20):
        """Get requests assigned to accountant"""
        query = ServiceRequest.query.filter_by(assigned_accountant_id=accountant_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_all_requests(self, status: str = None, page: int = 1, per_page: int = 20):
        """Get all requests (super admin view)"""
        query = ServiceRequest.query
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_requests_by_company(self, company_id: str, status: str = None,
                                 page: int = 1, per_page: int = 20):
        """Get requests from users in a specific company (admin view)"""
        query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
            .filter(User.company_id == company_id)
        if status:
            query = query.filter(ServiceRequest.status == status)
        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_requests_for_role(self, user: User, status: str = None,
                               page: int = 1, per_page: int = 20,
                               company_id: str = None, service_id: int = None,
                               invoice_status: str = None, date_from: str = None,
                               date_to: str = None, search: str = None,
                               accountant_id: str = None, user_id: str = None):
        """Get requests based on user role with advanced filters"""
        # Build base query based on role
        if user.role.name == Role.USER:
            query = ServiceRequest.query.filter_by(user_id=user.id)
        elif user.role.name == Role.ACCOUNTANT:
            # Accountants can see all requests in their company (same as admin)
            query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                .filter(User.company_id == user.company_id)
        elif user.role.name == Role.ADMIN:
            query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                .filter(User.company_id == user.company_id)
        else:
            # Super Admin
            if company_id:
                query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                    .filter(User.company_id == company_id)
            else:
                query = ServiceRequest.query

        # Exclude drafts from normal listing unless explicitly filtering by draft status
        if status != 'draft':
            query = query.filter(ServiceRequest.status != ServiceRequest.STATUS_DRAFT)

        # Apply common filters
        query = self._apply_filters(
            query, status, service_id, invoice_status,
            date_from, date_to, search, accountant_id, user_id
        )

        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def _apply_filters(self, query, status: str = None, service_id: int = None,
                       invoice_status: str = None, date_from: str = None,
                       date_to: str = None, search: str = None,
                       accountant_id: str = None, user_id: str = None):
        """Apply common filters to a query"""
        # Status filter
        if status:
            query = query.filter(ServiceRequest.status == status)

        # Service type filter
        if service_id:
            query = query.filter(ServiceRequest.service_id == service_id)

        # User (client) filter - filter by specific user who created the request
        if user_id:
            query = query.filter(ServiceRequest.user_id == user_id)

        # Invoice status filter
        if invoice_status:
            if invoice_status == 'not_raised':
                query = query.filter(
                    or_(ServiceRequest.invoice_raised == False,
                        ServiceRequest.invoice_raised.is_(None))
                )
            elif invoice_status == 'pending':
                query = query.filter(
                    ServiceRequest.invoice_raised == True,
                    or_(ServiceRequest.invoice_paid == False,
                        ServiceRequest.invoice_paid.is_(None))
                )
            elif invoice_status == 'paid':
                query = query.filter(
                    ServiceRequest.invoice_raised == True,
                    ServiceRequest.invoice_paid == True
                )

        # Date range filters
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(ServiceRequest.created_at >= from_date)
            except (ValueError, AttributeError):
                pass

        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(ServiceRequest.created_at <= to_date)
            except (ValueError, AttributeError):
                pass

        # Search filter (client name or Xero job ID)
        if search:
            search_term = f'%{search}%'
            # Need to join User if not already joined
            query = query.filter(
                or_(
                    ServiceRequest.xero_reference_job_id.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )

        # Accountant filter
        if accountant_id:
            query = query.filter(ServiceRequest.assigned_accountant_id == accountant_id)

        return query

    def get_pending_count(self) -> int:
        """Get count of pending requests"""
        return ServiceRequest.query.filter_by(status=ServiceRequest.STATUS_PENDING).count()

    def get_overdue_requests(self, company_id: str = None) -> List[ServiceRequest]:
        """Get requests that are past their deadline"""
        from datetime import date
        query = ServiceRequest.query.filter(
            ServiceRequest.deadline_date < date.today(),
            ServiceRequest.status != ServiceRequest.STATUS_COMPLETED
        )
        if company_id:
            query = query.join(User, ServiceRequest.user_id == User.id)\
                .filter(User.company_id == company_id)
        return query.order_by(ServiceRequest.deadline_date.asc()).all()

    def get_by_client_entity(self, client_entity_id: str, page: int = 1, per_page: int = 20):
        """Get requests for a specific client entity"""
        query = ServiceRequest.query.filter_by(client_entity_id=client_entity_id)
        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def can_user_access_request(self, user: User, request: 'ServiceRequest') -> bool:
        """
        Check if user can access a specific request based on role and company.

        - Super Admin: Can access all requests
        - Admin: Can access requests from users in their company
        - Accountant: Can access only their assigned requests
        - User: Can access only their own requests
        """
        if user.role.name == Role.SUPER_ADMIN:
            return True
        elif user.role.name == Role.ADMIN:
            # Admin can access requests from users in same company
            return request.user.company_id == user.company_id
        elif user.role.name == Role.ACCOUNTANT:
            # Accountant can access requests from users in same company
            return request.user.company_id == user.company_id
        else:
            return request.user_id == user.id

    def get_dashboard_stats(self, user: User, company_id: str = None) -> Dict[str, Any]:
        """Get dashboard statistics based on user role (excludes drafts)"""
        if user.role.name == Role.SUPER_ADMIN:
            if company_id:
                query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                    .filter(User.company_id == company_id)
            else:
                query = ServiceRequest.query
        elif user.role.name in [Role.ADMIN, Role.ACCOUNTANT]:
            # Both admin and accountant see all requests in their company
            query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)\
                .filter(User.company_id == user.company_id)
        else:
            query = ServiceRequest.query.filter_by(user_id=user.id)

        # Exclude drafts from dashboard stats
        requests = query.filter(ServiceRequest.status != ServiceRequest.STATUS_DRAFT).all()

        return {
            'total': len(requests),
            'pending': sum(1 for r in requests if r.status in [
                ServiceRequest.STATUS_PENDING,
                ServiceRequest.STATUS_INVOICE_RAISED,
                ServiceRequest.STATUS_ASSIGNED
            ]),
            'processing': sum(1 for r in requests if r.status == ServiceRequest.STATUS_PROCESSING),
            'completed': sum(1 for r in requests if r.status == ServiceRequest.STATUS_COMPLETED),
            'queries': sum(1 for r in requests if r.status == ServiceRequest.STATUS_QUERY_RAISED),
            'invoices_raised': sum(1 for r in requests if r.invoice_raised),
            'invoices_paid': sum(1 for r in requests if r.invoice_paid),
            'total_revenue': sum(r.invoice_amount or 0 for r in requests if r.invoice_paid),
        }
