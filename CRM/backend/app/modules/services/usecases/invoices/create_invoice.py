"""
Create Invoice Use Case
"""
from decimal import Decimal
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice, InvoiceLineItem
from app.modules.user.models import User, Role


class CreateInvoiceUseCase(BaseCommandUseCase):
    """
    Create a new invoice with line items.

    Business Rules:
    - Client must exist and belong to the same company
    - Generates unique invoice number
    - Calculates totals automatically
    - Creates invoice in draft status
    """

    def execute(self, company_id: str, created_by_id: str, client_id: str,
                due_date, line_items: list, service_request_id: str = None,
                reference: str = None, tax_rate: float = 10,
                discount_amount: float = 0, discount_description: str = None,
                notes: str = None, payment_terms: str = None) -> UseCaseResult:
        """
        Create a new invoice.

        Args:
            company_id: ID of the company creating the invoice
            created_by_id: ID of the user creating the invoice
            client_id: ID of the client
            due_date: Invoice due date
            line_items: List of line item dictionaries
            service_request_id: Optional linked service request ID
            reference: Optional reference/PO number
            tax_rate: Tax rate (default 10%)
            discount_amount: Discount amount
            discount_description: Discount description
            notes: Notes visible to client
            payment_terms: Payment terms

        Returns:
            UseCaseResult with created invoice
        """
        # Verify client exists
        client = User.query.get(client_id)
        if not client:
            return UseCaseResult.fail('Client not found', 'NOT_FOUND')

        # Verify client belongs to same company (unless super admin)
        creator = User.query.get(created_by_id)
        if creator and creator.role.name != Role.SUPER_ADMIN:
            if client.company_id != company_id:
                return UseCaseResult.fail('Client does not belong to your company', 'FORBIDDEN')

        # Generate invoice number
        invoice_number = Invoice.generate_invoice_number(company_id)

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            reference=reference,
            company_id=company_id,
            client_id=client_id,
            service_request_id=service_request_id,
            due_date=due_date,
            tax_rate=Decimal(str(tax_rate)),
            discount_amount=Decimal(str(discount_amount)),
            discount_description=discount_description,
            notes=notes,
            payment_terms=payment_terms,
            created_by_id=created_by_id,
            status=Invoice.STATUS_DRAFT
        )
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID

        # Add line items
        for idx, item_data in enumerate(line_items):
            quantity = Decimal(str(item_data.get('quantity', 1)))
            unit_price = Decimal(str(item_data['unit_price']))
            total = quantity * unit_price

            line_item = InvoiceLineItem(
                invoice_id=invoice.id,
                description=item_data['description'],
                quantity=quantity,
                unit_price=unit_price,
                total=total,
                service_id=item_data.get('service_id'),
                is_tax_exempt=item_data.get('is_tax_exempt', False),
                order=idx
            )
            db.session.add(line_item)

        db.session.flush()

        # Calculate totals
        invoice.calculate_totals()
        db.session.commit()

        return UseCaseResult.ok({
            'invoice': invoice.to_dict(include_items=True)
        })
