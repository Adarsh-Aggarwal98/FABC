"""
Invoice Routes - API Endpoints for Invoice Management

This module provides REST API endpoints for invoice CRUD operations,
sending invoices to clients, and recording payments.

Endpoints:
---------
GET  /api/services/invoices
    List invoices (filtered by company for staff, own invoices for clients).
    Query params: status, client_id, page, per_page
    Required role: Any authenticated user

POST /api/services/invoices
    Create a new invoice.
    Required role: Admin or Accountant

GET  /api/services/invoices/<invoice_id>
    Get invoice details with line items.
    Required role: Staff or invoice client

PATCH /api/services/invoices/<invoice_id>
    Update invoice details (draft/sent invoices only).
    Required role: Admin or Accountant

POST /api/services/invoices/<invoice_id>/send
    Send invoice to client (sends email notification).
    Required role: Admin or Accountant

POST /api/services/invoices/<invoice_id>/cancel
    Cancel an invoice.
    Required role: Admin or Accountant

POST /api/services/invoices/<invoice_id>/payments
    Record a payment for an invoice.
    Required role: Admin or Accountant

Security Notes:
--------------
- Clients can only view their own invoices
- Staff members are scoped to their company
- Super admin can access any invoice
"""
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError

from app.modules.services.usecases.invoices import (
    CreateInvoiceUseCase,
    UpdateInvoiceDetailsUseCase,
    GetInvoiceUseCase,
    ListInvoicesUseCase,
    SendInvoiceUseCase,
    AddInvoicePaymentUseCase,
    CancelInvoiceUseCase,
)
from app.modules.services.schemas.invoice_schemas import (
    CreateInvoiceSchema,
    UpdateInvoiceDetailsSchema,
    AddInvoicePaymentSchema,
    SendInvoiceSchema,
)
from app.common.decorators import accountant_required, invoice_admin_required, get_current_user
from app.common.responses import success_response, error_response

# Module-level logger
logger = logging.getLogger(__name__)

# Create blueprint
invoices_bp = Blueprint('invoices', __name__)


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
        'INVALID_STATUS': 400,
        'AMOUNT_EXCEEDS_BALANCE': 400,
        'ALREADY_CANCELLED': 400,
    }
    return status_map.get(error_code, 400)


@invoices_bp.route('', methods=['GET'])
@jwt_required()
def list_invoices():
    """
    List invoices.

    Staff sees company invoices, clients see their own invoices.
    """
    user = get_current_user()
    logger.info(f"GET /services/invoices - List invoices by user_id={user.id}")

    status = request.args.get('status')
    client_id = request.args.get('client_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    usecase = ListInvoicesUseCase()
    result = usecase.execute(
        user_id=user.id,
        company_id=user.company_id,
        client_id=client_id,
        status=status,
        page=page,
        per_page=per_page
    )

    if result.success:
        logger.debug(f"Retrieved {len(result.data.get('invoices', []))} invoices")
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@invoices_bp.route('', methods=['POST'])
@jwt_required()
@invoice_admin_required
def create_invoice():
    """
    Create a new invoice.

    Required fields: client_id, due_date, line_items
    Each line_item needs: description, unit_price, quantity (optional)
    """
    user = get_current_user()
    logger.info(f"POST /services/invoices - Create invoice by user_id={user.id}")

    try:
        schema = CreateInvoiceSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        logger.warning(f"Invoice validation error: {e.messages}")
        return error_response('Validation error', errors=e.messages)

    usecase = CreateInvoiceUseCase()
    result = usecase.execute(
        company_id=user.company_id,
        created_by_id=user.id,
        client_id=data['client_id'],
        due_date=data['due_date'],
        line_items=data['line_items'],
        service_request_id=data.get('service_request_id'),
        reference=data.get('reference'),
        tax_rate=data.get('tax_rate', 10),
        discount_amount=data.get('discount_amount', 0),
        discount_description=data.get('discount_description'),
        notes=data.get('notes'),
        payment_terms=data.get('payment_terms')
    )

    if result.success:
        logger.info(f"Invoice created: {result.data['invoice'].get('invoice_number')}")
        return success_response(result.data, message='Invoice created successfully', status_code=201)
    logger.warning(f"Invoice creation failed: {result.error}")
    return error_response(result.error, _get_status_code(result.error_code))


@invoices_bp.route('/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get invoice details with line items."""
    user = get_current_user()
    logger.info(f"GET /services/invoices/{invoice_id} - Get invoice by user_id={user.id}")

    include_payments = request.args.get('include_payments', 'false').lower() == 'true'

    usecase = GetInvoiceUseCase()
    result = usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
        include_payments=include_payments
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@invoices_bp.route('/<invoice_id>', methods=['PATCH'])
@jwt_required()
@invoice_admin_required
def update_invoice(invoice_id):
    """Update invoice details (draft/sent invoices only)."""
    user = get_current_user()
    logger.info(f"PATCH /services/invoices/{invoice_id} - Update invoice by user_id={user.id}")

    try:
        schema = UpdateInvoiceDetailsSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    usecase = UpdateInvoiceDetailsUseCase()
    result = usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
        data=data
    )

    if result.success:
        logger.info(f"Invoice {invoice_id} updated successfully")
        return success_response(result.data, message='Invoice updated successfully')
    return error_response(result.error, _get_status_code(result.error_code))


@invoices_bp.route('/<invoice_id>/send', methods=['POST'])
@jwt_required()
@invoice_admin_required
def send_invoice(invoice_id):
    """Send invoice to client via email."""
    user = get_current_user()
    logger.info(f"POST /services/invoices/{invoice_id}/send - Send invoice by user_id={user.id}")

    data = request.get_json(silent=True) or {}
    send_email = data.get('send_email', True)
    email_message = data.get('email_message')

    usecase = SendInvoiceUseCase()
    result = usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
        send_email=send_email,
        email_message=email_message
    )

    if result.success:
        logger.info(f"Invoice {invoice_id} sent successfully")
        return success_response(result.data, message='Invoice sent successfully')
    return error_response(result.error, _get_status_code(result.error_code))


@invoices_bp.route('/<invoice_id>/cancel', methods=['POST'])
@jwt_required()
@invoice_admin_required
def cancel_invoice(invoice_id):
    """Cancel an invoice."""
    user = get_current_user()
    logger.info(f"POST /services/invoices/{invoice_id}/cancel - Cancel invoice by user_id={user.id}")

    data = request.get_json(silent=True) or {}
    reason = data.get('reason')

    usecase = CancelInvoiceUseCase()
    result = usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
        reason=reason
    )

    if result.success:
        logger.info(f"Invoice {invoice_id} cancelled")
        return success_response(result.data, message='Invoice cancelled')
    return error_response(result.error, _get_status_code(result.error_code))


@invoices_bp.route('/<invoice_id>/payments', methods=['POST'])
@jwt_required()
@invoice_admin_required
def add_payment(invoice_id):
    """Record a payment for an invoice."""
    user = get_current_user()
    logger.info(f"POST /services/invoices/{invoice_id}/payments - Add payment by user_id={user.id}")

    try:
        schema = AddInvoicePaymentSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    usecase = AddInvoicePaymentUseCase()
    result = usecase.execute(
        invoice_id=invoice_id,
        user_id=user.id,
        amount=float(data['amount']),
        payment_method=data.get('payment_method', 'card'),
        reference=data.get('reference'),
        notes=data.get('notes'),
        payment_date=data.get('payment_date')
    )

    if result.success:
        logger.info(f"Payment recorded for invoice {invoice_id}")
        return success_response(result.data, message='Payment recorded', status_code=201)
    return error_response(result.error, _get_status_code(result.error_code))
