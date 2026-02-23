"""
Payment Routes - API Endpoints for Stripe payment integration

This module provides REST API endpoints for payment processing using Stripe.
It supports checkout sessions, payment intents, webhooks, and payment links.

Endpoints:
---------
GET  /api/payments/config
    Get Stripe publishable key for frontend initialization.
    Required role: Any authenticated user

POST /api/payments/invoices/<invoice_id>/checkout
    Create a Stripe Checkout Session for an invoice.
    Required role: Client (own invoices) or Staff (any invoice)
    Body: { success_url, cancel_url }

POST /api/payments/invoices/<invoice_id>/payment-intent
    Create a Stripe Payment Intent for embedded payment forms.
    Required role: Client (own invoices) or Staff (any invoice)

GET  /api/payments/checkout-session/<session_id>
    Retrieve status of a checkout session.
    Required role: Any authenticated user

GET  /api/payments/payment-intent/<intent_id>
    Retrieve status of a payment intent.
    Required role: Any authenticated user

POST /api/payments/webhooks/stripe
    Handle Stripe webhook events (payment completed, failed, refunded).
    No authentication - Stripe signature verification

POST /api/payments/invoices/<invoice_id>/payment-link
    Generate a shareable payment link for an invoice.
    Required role: Staff only

GET  /api/payments/customer/payment-methods
    Get saved payment methods for current user.
    Required role: Any authenticated user

GET  /api/payments/invoices/<invoice_id>/payments
    Get payment history for an invoice.
    Required role: Client (own invoices) or Staff (any invoice)

Security Notes:
--------------
- Webhook endpoint uses Stripe signature verification instead of JWT
- Payment methods are scoped to the authenticated user's Stripe customer ID
- Staff roles can generate payment links; clients can only pay their own invoices
"""
import logging

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.modules.payments import payments_bp

# Module-level logger
logger = logging.getLogger(__name__)
from app.modules.payments.services import StripeService
from app.modules.services.models import Invoice
from app.modules.user.models import User, Role
from app.common.decorators import get_current_user
from app.common.responses import success_response, error_response


@payments_bp.route('/config', methods=['GET'])
@jwt_required()
def get_stripe_config():
    """
    Get Stripe publishable key for frontend.

    Returns the public Stripe key required for initializing Stripe.js
    on the client side. This is safe to expose publicly.
    """
    logger.debug("GET /payments/config - Fetching Stripe publishable key")
    try:
        public_key = StripeService.get_public_key()
        logger.info("Stripe config retrieved successfully")
        return success_response({
            'publishable_key': public_key
        })
    except Exception as e:
        logger.error(f"Failed to get Stripe config: {str(e)}")
        return error_response(f'Failed to get Stripe config: {str(e)}', 500)


@payments_bp.route('/invoices/<invoice_id>/checkout', methods=['POST'])
@jwt_required()
def create_checkout_session(invoice_id):
    """
    Create a Stripe Checkout Session for an invoice.

    This creates a Stripe-hosted checkout page where the client can
    enter payment details. After payment, they're redirected to success_url.

    Request body:
    - success_url: URL to redirect after successful payment
    - cancel_url: URL to redirect if payment is cancelled

    Returns:
    - checkout_url: URL to redirect user to Stripe checkout
    - session_id: Stripe session ID for tracking
    """
    logger.info(f"POST /payments/invoices/{invoice_id}/checkout - Creating checkout session")
    user = get_current_user()
    if not user:
        return error_response('User not found', 401)

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return error_response('Invoice not found', 404)

    # Check permission - client can pay their own invoices, admin can create for anyone
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
        if invoice.client_id != user.id:
            return error_response('Access denied', 403)

    # Check invoice status
    if invoice.status == Invoice.STATUS_PAID:
        return error_response('Invoice is already paid', 400)

    if invoice.status == Invoice.STATUS_CANCELLED:
        return error_response('Invoice is cancelled', 400)

    if invoice.status == Invoice.STATUS_DRAFT:
        return error_response('Invoice has not been sent yet', 400)

    data = request.get_json(silent=True) or {}
    success_url = data.get('success_url')
    cancel_url = data.get('cancel_url')

    if not success_url or not cancel_url:
        return error_response('success_url and cancel_url are required', 400)

    try:
        logger.debug(f"Creating Stripe checkout session for invoice_id={invoice_id}, user_id={user.id}")
        result = StripeService.create_checkout_session(
            invoice=invoice,
            success_url=success_url,
            cancel_url=cancel_url
        )
        logger.info(f"Checkout session created successfully for invoice_id={invoice_id}")
        return success_response(result)
    except ValueError as e:
        logger.warning(f"Checkout session validation error for invoice_id={invoice_id}: {str(e)}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Failed to create checkout session for invoice_id={invoice_id}: {str(e)}")
        return error_response(f'Failed to create checkout session: {str(e)}', 500)


@payments_bp.route('/invoices/<invoice_id>/payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent(invoice_id):
    """
    Create a Stripe Payment Intent for custom payment flow.

    Use this for embedded payment forms instead of Checkout redirect.
    """
    user = get_current_user()
    if not user:
        return error_response('User not found', 401)

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return error_response('Invoice not found', 404)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
        if invoice.client_id != user.id:
            return error_response('Access denied', 403)

    # Check invoice status
    if invoice.status == Invoice.STATUS_PAID:
        return error_response('Invoice is already paid', 400)

    if invoice.status == Invoice.STATUS_CANCELLED:
        return error_response('Invoice is cancelled', 400)

    if invoice.balance_due <= 0:
        return error_response('No balance due on invoice', 400)

    try:
        result = StripeService.create_payment_intent(invoice)
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to create payment intent: {str(e)}', 500)


@payments_bp.route('/checkout-session/<session_id>', methods=['GET'])
@jwt_required()
def get_checkout_session(session_id):
    """Get status of a checkout session"""
    try:
        result = StripeService.retrieve_checkout_session(session_id)
        return success_response(result)
    except Exception as e:
        return error_response(f'Failed to retrieve session: {str(e)}', 500)


@payments_bp.route('/payment-intent/<intent_id>', methods=['GET'])
@jwt_required()
def get_payment_intent(intent_id):
    """Get status of a payment intent"""
    try:
        result = StripeService.retrieve_payment_intent(intent_id)
        return success_response(result)
    except Exception as e:
        return error_response(f'Failed to retrieve payment intent: {str(e)}', 500)


@payments_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhooks.

    This endpoint receives events from Stripe when payments are completed,
    failed, refunded, etc. Common event types:
    - checkout.session.completed: Checkout payment successful
    - payment_intent.succeeded: Payment intent completed
    - payment_intent.payment_failed: Payment failed
    - charge.refunded: Refund processed

    Note: No JWT authentication required - Stripe signs the payload
    using a webhook secret for verification.
    """
    logger.info("POST /payments/webhooks/stripe - Received Stripe webhook")
    payload = request.data
    signature = request.headers.get('Stripe-Signature')

    if not signature:
        logger.warning("Stripe webhook received without signature header")
        return jsonify({'error': 'Missing signature'}), 400

    try:
        logger.debug("Processing Stripe webhook event")
        result = StripeService.handle_webhook_event(payload, signature)
        logger.info(f"Stripe webhook processed successfully: {result.get('event_type', 'unknown')}")
        return jsonify(result), 200
    except ValueError as e:
        logger.warning(f"Stripe webhook validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Stripe webhook handling failed: {str(e)}")
        return jsonify({'error': f'Webhook handling failed: {str(e)}'}), 500


@payments_bp.route('/invoices/<invoice_id>/payment-link', methods=['POST'])
@jwt_required()
def generate_payment_link(invoice_id):
    """
    Generate a shareable payment link for an invoice.

    This creates a checkout session with a preset URL and returns
    a shareable link that can be sent to the client.
    """
    user = get_current_user()
    if not user:
        return error_response('User not found', 401)

    # Only staff can generate payment links
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
        return error_response('Access denied', 403)

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return error_response('Invoice not found', 404)

    # Check company permission
    if user.role.name != Role.SUPER_ADMIN and invoice.company_id != user.company_id:
        return error_response('Access denied', 403)

    if invoice.status in [Invoice.STATUS_PAID, Invoice.STATUS_CANCELLED]:
        return error_response(f'Cannot generate link for {invoice.status} invoice', 400)

    data = request.get_json(silent=True) or {}
    base_url = data.get('base_url', request.host_url.rstrip('/'))

    success_url = f"{base_url}/payment/success"
    cancel_url = f"{base_url}/payment/cancelled"

    try:
        result = StripeService.create_checkout_session(
            invoice=invoice,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return success_response({
            'payment_link': result['checkout_url'],
            'expires_at': result['expires_at'],
            'invoice_id': invoice_id
        })
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to generate payment link: {str(e)}', 500)


@payments_bp.route('/customer/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get saved payment methods for the current user"""
    user = get_current_user()
    if not user:
        return error_response('User not found', 401)

    if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
        return success_response({'payment_methods': []})

    try:
        methods = StripeService.list_payment_methods(user.stripe_customer_id)
        return success_response({'payment_methods': methods})
    except Exception as e:
        return error_response(f'Failed to retrieve payment methods: {str(e)}', 500)


@payments_bp.route('/invoices/<invoice_id>/payments', methods=['GET'])
@jwt_required()
def get_invoice_payments(invoice_id):
    """Get payment history for an invoice"""
    user = get_current_user()
    if not user:
        return error_response('User not found', 401)

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return error_response('Invoice not found', 404)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
        if invoice.client_id != user.id:
            return error_response('Access denied', 403)
    elif user.role.name != Role.SUPER_ADMIN and invoice.company_id != user.company_id:
        return error_response('Access denied', 403)

    payments = [
        {
            'id': p.id,
            'amount': float(p.amount) if p.amount else 0,
            'payment_method': p.payment_method,
            'reference': p.reference,
            'status': p.status,
            'payment_date': p.payment_date.isoformat() if p.payment_date else None,
            'notes': p.notes
        }
        for p in invoice.payments
    ]

    return success_response({
        'invoice_id': invoice_id,
        'payments': payments,
        'total_paid': float(invoice.amount_paid) if invoice.amount_paid else 0,
        'balance_due': float(invoice.balance_due) if invoice.balance_due else 0
    })
