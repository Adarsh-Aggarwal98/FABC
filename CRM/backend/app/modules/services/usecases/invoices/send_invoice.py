"""
Send Invoice Use Case
"""
from datetime import datetime
from flask import current_app
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Invoice, ServiceRequest
from app.modules.user.models import User, Role


class SendInvoiceUseCase(BaseCommandUseCase):
    """
    Send an invoice to the client.

    Business Rules:
    - Invoice must be in draft or sent status
    - Sends email notification
    - Updates status to 'sent'
    """

    def execute(self, invoice_id: str, user_id: str,
                send_email: bool = True, email_message: str = None) -> UseCaseResult:
        """
        Send an invoice to the client.

        Args:
            invoice_id: ID of the invoice to send
            user_id: ID of the user sending the invoice
            send_email: Whether to send email notification
            email_message: Custom message for the email

        Returns:
            UseCaseResult with sent invoice
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return UseCaseResult.fail('Invoice not found', 'NOT_FOUND')

        if invoice.status not in [Invoice.STATUS_DRAFT, Invoice.STATUS_SENT]:
            return UseCaseResult.fail('Cannot send this invoice', 'INVALID_STATUS')

        # Check permission
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and user.company_id != invoice.company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        # Update status
        invoice.status = Invoice.STATUS_SENT
        invoice.sent_at = datetime.utcnow()

        # Link to service request if exists
        if invoice.service_request_id:
            service_request = ServiceRequest.query.get(invoice.service_request_id)
            if service_request:
                service_request.invoice_raised = True
                service_request.invoice_amount = invoice.total

        db.session.commit()

        # Send email notification
        if send_email:
            try:
                from app.modules.notifications.services import NotificationService
                NotificationService.send_invoice_email(
                    invoice=invoice,
                    custom_message=email_message
                )
            except Exception as e:
                current_app.logger.error(f'Failed to send invoice email: {str(e)}')

        return UseCaseResult.ok({
            'invoice': invoice.to_dict(include_items=True),
            'message': 'Invoice sent successfully'
        })
