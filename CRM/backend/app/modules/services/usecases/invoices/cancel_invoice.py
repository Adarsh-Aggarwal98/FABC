"""
Cancel Invoice Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice
from app.modules.user.models import User, Role


class CancelInvoiceUseCase(BaseCommandUseCase):
    """Cancel an invoice"""

    def execute(self, invoice_id: str, user_id: str, reason: str = None) -> UseCaseResult:
        """
        Cancel an invoice.

        Args:
            invoice_id: ID of the invoice to cancel
            user_id: ID of the user cancelling the invoice
            reason: Optional reason for cancellation

        Returns:
            UseCaseResult with cancelled invoice
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        if invoice.status == Invoice.STATUS_PAID:
            return UseCaseResult.fail('Cannot cancel a paid invoice', 'INVALID_STATUS')

        if invoice.status == Invoice.STATUS_CANCELLED:
            return UseCaseResult.fail('Invoice is already cancelled', 'ALREADY_CANCELLED')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and user.company_id != invoice.company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        invoice.status = Invoice.STATUS_CANCELLED
        if reason:
            invoice.internal_notes = (invoice.internal_notes or '') + f"\nCancelled: {reason}"

        db.session.commit()

        return UseCaseResult.ok({
            'invoice': invoice.to_dict(),
            'message': 'Invoice cancelled'
        })
