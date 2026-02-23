"""
Update Invoice Details Use Case
"""
from decimal import Decimal
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice
from app.modules.user.models import User, Role


class UpdateInvoiceDetailsUseCase(BaseCommandUseCase):
    """Update invoice details (not line items)"""

    def execute(self, invoice_id: str, user_id: str, data: dict) -> UseCaseResult:
        """
        Update invoice details.

        Args:
            invoice_id: ID of the invoice to update
            user_id: ID of the user making the update
            data: Dictionary of fields to update

        Returns:
            UseCaseResult with updated invoice
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        # Only draft invoices can be edited
        if invoice.status not in [Invoice.STATUS_DRAFT, Invoice.STATUS_SENT]:
            return UseCaseResult.fail('Only draft or sent invoices can be edited', 'INVALID_STATUS')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and user.company_id != invoice.company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        # Update fields
        updateable_fields = ['reference', 'due_date', 'notes', 'internal_notes', 'payment_terms']
        for field in updateable_fields:
            if field in data:
                setattr(invoice, field, data[field])

        if 'tax_rate' in data:
            invoice.tax_rate = Decimal(str(data['tax_rate']))
        if 'discount_amount' in data:
            invoice.discount_amount = Decimal(str(data['discount_amount']))
        if 'discount_description' in data:
            invoice.discount_description = data['discount_description']

        invoice.calculate_totals()
        db.session.commit()

        return UseCaseResult.ok({
            'invoice': invoice.to_dict(include_items=True)
        })
