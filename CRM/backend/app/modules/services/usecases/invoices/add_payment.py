"""
Add Invoice Payment Use Case
"""
from decimal import Decimal
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice, ServiceRequest
from app.modules.user.models import User, Role


class AddInvoicePaymentUseCase(BaseCommandUseCase):
    """
    Record a payment for an invoice.

    Business Rules:
    - Updates paid amount and balance due
    - Marks invoice as paid if fully paid
    - Updates linked service request if exists
    """

    def execute(self, invoice_id: str, user_id: str, amount: float,
                payment_method: str = 'card', reference: str = None,
                notes: str = None, payment_date=None) -> UseCaseResult:
        """
        Record a payment for an invoice.

        Args:
            invoice_id: ID of the invoice
            user_id: ID of the user recording the payment
            amount: Payment amount
            payment_method: Payment method (card, bank_transfer, etc.)
            reference: Optional payment reference
            notes: Optional notes
            payment_date: Optional payment date

        Returns:
            UseCaseResult with payment and updated invoice
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        if invoice.status == Invoice.STATUS_CANCELLED:
            return UseCaseResult.fail('Cannot add payment to cancelled invoice', 'INVALID_STATUS')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and user.company_id != invoice.company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        amount_dec = Decimal(str(amount))

        if amount_dec > invoice.balance_due:
            return UseCaseResult.fail(
                f'Payment amount ({amount}) exceeds balance due ({invoice.balance_due})',
                'AMOUNT_EXCEEDS_BALANCE'
            )

        # Add payment
        payment = invoice.add_payment(
            amount=amount_dec,
            method=payment_method,
            reference=reference,
            notes=notes
        )

        if payment_date:
            payment.payment_date = payment_date

        # Update linked service request if fully paid
        if invoice.status == Invoice.STATUS_PAID and invoice.service_request_id:
            service_request = ServiceRequest.query.get(invoice.service_request_id)
            if service_request:
                service_request.invoice_paid = True

        db.session.commit()

        return UseCaseResult.ok({
            'payment': payment.to_dict(),
            'invoice': invoice.to_dict(include_items=True, include_payments=True)
        })
