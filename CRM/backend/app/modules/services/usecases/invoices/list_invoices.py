"""
List Invoices Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.models import Invoice
from app.modules.user.models import User, Role


class ListInvoicesUseCase(BaseQueryUseCase):
    """List invoices with filters"""

    def execute(self, user_id: str, company_id: str = None, client_id: str = None,
                status: str = None, page: int = 1, per_page: int = 20) -> UseCaseResult:
        """
        List invoices with optional filters.

        Args:
            user_id: ID of the requesting user
            company_id: Optional company filter
            client_id: Optional client filter
            status: Optional status filter
            page: Page number
            per_page: Items per page

        Returns:
            UseCaseResult with paginated list of invoices
        """
        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        query = Invoice.query

        # Filter by company
        if user.role.name == Role.SUPER_ADMIN:
            if company_id:
                query = query.filter_by(company_id=company_id)
        elif user.role.name in [Role.ADMIN, Role.ACCOUNTANT]:
            query = query.filter_by(company_id=user.company_id)
        else:
            # Client can only see their own invoices
            query = query.filter_by(client_id=user.id)

        # Filter by client
        if client_id and user.role.name != Role.USER:
            query = query.filter_by(client_id=client_id)

        # Filter by status
        if status:
            query = query.filter_by(status=status)

        # Order by most recent
        query = query.order_by(Invoice.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return UseCaseResult.ok({
            'invoices': [inv.to_dict(include_items=False) for inv in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
