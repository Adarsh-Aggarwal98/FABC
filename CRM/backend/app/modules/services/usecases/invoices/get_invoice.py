"""
Get Invoice Use Case
"""
from datetime import datetime
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice
from app.modules.user.models import User, Role


class GetInvoiceUseCase(BaseQueryUseCase):
    """Get invoice by ID"""

    def execute(self, invoice_id: str, user_id: str, include_payments: bool = False) -> UseCaseResult:
        """
        Get an invoice by ID.

        Args:
            invoice_id: ID of the invoice
            user_id: ID of the user requesting the invoice
            include_payments: Whether to include payment history

        Returns:
            UseCaseResult with invoice data
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name == Role.SUPER_ADMIN:
            pass  # Can view any invoice
        elif user.role.name in [Role.ADMIN, Role.ACCOUNTANT]:
            if user.company_id != invoice.company_id:
                return UseCaseResult.fail('Access denied', 'FORBIDDEN')
        else:
            # Client can only view their own invoices
            if user.id != invoice.client_id:
                return UseCaseResult.fail('Access denied', 'FORBIDDEN')
            # Mark as viewed
            if not invoice.viewed_at:
                invoice.viewed_at = datetime.utcnow()
                if invoice.status == Invoice.STATUS_SENT:
                    invoice.status = Invoice.STATUS_VIEWED
                db.session.commit()

        return UseCaseResult.ok({
            'invoice': invoice.to_dict(include_items=True, include_payments=include_payments)
        })
