"""
Update Invoice Details Use Case
"""
from flask import current_app
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ServiceRequest
from app.modules.services.repositories import ServiceRequestRepository
from app.modules.user.repositories import UserRepository


class UpdateInvoiceUseCase(BaseCommandUseCase):
    """
    Update invoice details.

    Business Rules:
    - Admin can only update invoices within their company
    - Super Admin can update any invoice
    - When invoice_raised is True:
      - Update status to INVOICE_RAISED (if pending)
      - Notify user about invoice
    - When invoice_paid is True, update status to PROCESSING
    """

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, updated_by_id: str, invoice_raised: bool = None,
                invoice_paid: bool = None, invoice_amount: float = None,
                payment_link: str = None) -> UseCaseResult:
        """
        Update invoice details for a service request.

        Args:
            request_id: ID of the request to update
            updated_by_id: ID of the user making the change
            invoice_raised: Whether invoice has been raised
            invoice_paid: Whether invoice has been paid
            invoice_amount: Invoice amount
            payment_link: Payment link URL

        Returns:
            UseCaseResult with updated request
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        # Check if user can access this request
        updated_by = self.user_repo.get_by_id(updated_by_id)
        if not updated_by:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not self.request_repo.can_user_access_request(updated_by, request):
            return UseCaseResult.fail('Access denied to this request', 'FORBIDDEN')

        if invoice_raised is not None:
            request.invoice_raised = invoice_raised
            if invoice_raised:
                # Update status to invoice_raised if currently pending
                if request.status == ServiceRequest.STATUS_PENDING:
                    request.status = ServiceRequest.STATUS_INVOICE_RAISED
                self._notify_invoice(request)

        if invoice_paid is not None:
            request.invoice_paid = invoice_paid
            if invoice_paid:
                # Only move to processing if already assigned to an accountant
                # Otherwise stay at invoice_raised (ready for assignment)
                if request.assigned_accountant_id:
                    request.status = ServiceRequest.STATUS_PROCESSING
                # If not assigned, status stays at invoice_raised (or current status)

        if invoice_amount is not None:
            request.invoice_amount = invoice_amount

        if payment_link is not None:
            request.payment_link = payment_link

        db.session.commit()
        return UseCaseResult.ok({'request': request.to_dict(include_notes=True)})

    def _notify_invoice(self, request: ServiceRequest):
        """Send invoice notification to user"""
        try:
            from app.modules.notifications.services import NotificationService
            NotificationService.send_invoice_notification(request)
        except Exception as e:
            current_app.logger.error(f'Failed to send invoice notification: {str(e)}')
