"""
Add Invoice Line Item Use Case
"""
from decimal import Decimal
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice, InvoiceLineItem
from app.modules.user.models import User, Role


class AddInvoiceLineItemUseCase(BaseCommandUseCase):
    """Add a line item to an invoice"""

    def execute(self, invoice_id: str, user_id: str, description: str,
                unit_price: float, quantity: float = 1,
                service_id: int = None, is_tax_exempt: bool = False) -> UseCaseResult:
        """
        Add a line item to an invoice.

        Args:
            invoice_id: ID of the invoice
            user_id: ID of the user making the change
            description: Item description
            unit_price: Unit price
            quantity: Quantity (default 1)
            service_id: Optional service ID
            is_tax_exempt: Whether item is tax exempt

        Returns:
            UseCaseResult with line item and updated invoice
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        if invoice.status not in [Invoice.STATUS_DRAFT]:
            return UseCaseResult.fail('Can only add items to draft invoices', 'INVALID_STATUS')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and user.company_id != invoice.company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        # Get max order
        max_order = invoice.line_items.count()

        quantity_dec = Decimal(str(quantity))
        unit_price_dec = Decimal(str(unit_price))

        line_item = InvoiceLineItem(
            invoice_id=invoice_id,
            description=description,
            quantity=quantity_dec,
            unit_price=unit_price_dec,
            total=quantity_dec * unit_price_dec,
            service_id=service_id,
            is_tax_exempt=is_tax_exempt,
            order=max_order
        )
        db.session.add(line_item)

        invoice.calculate_totals()
        db.session.commit()

        return UseCaseResult.ok({
            'line_item': line_item.to_dict(),
            'invoice': invoice.to_dict(include_items=True)
        })
