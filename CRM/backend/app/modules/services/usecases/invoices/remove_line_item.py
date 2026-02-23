"""
Remove Invoice Line Item Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice, InvoiceLineItem
from app.modules.user.models import User, Role


class RemoveInvoiceLineItemUseCase(BaseCommandUseCase):
    """Remove a line item from an invoice"""

    def execute(self, invoice_id: str, line_item_id: int, user_id: str) -> UseCaseResult:
        """
        Remove a line item from an invoice.

        Args:
            invoice_id: ID of the invoice
            line_item_id: ID of the line item to remove
            user_id: ID of the user making the change

        Returns:
            UseCaseResult with updated invoice
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        if invoice.status != Invoice.STATUS_DRAFT:
            return UseCaseResult.fail('Can only remove items from draft invoices', 'INVALID_STATUS')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and user.company_id != invoice.company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        line_item = InvoiceLineItem.query.get(line_item_id)
        if not line_item or line_item.invoice_id != invoice_id:
            return UseCaseResult.fail('Line item not found', 'NOT_FOUND')

        db.session.delete(line_item)
        invoice.calculate_totals()
        db.session.commit()

        return UseCaseResult.ok({
            'message': 'Line item removed',
            'invoice': invoice.to_dict(include_items=True)
        })
