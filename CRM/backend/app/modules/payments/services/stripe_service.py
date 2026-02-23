"""
Stripe Payment Service - Handles all Stripe API interactions
"""
import stripe
from flask import current_app
from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.modules.services.models import Invoice, InvoicePayment


class StripeService:
    """Service for Stripe payment gateway integration"""

    @staticmethod
    def _init_stripe():
        """Initialize Stripe with API key from config"""
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        if not stripe.api_key:
            raise ValueError('STRIPE_SECRET_KEY not configured')

    @classmethod
    def create_checkout_session(
        cls,
        invoice: Invoice,
        success_url: str,
        cancel_url: str
    ) -> dict:
        """
        Create a Stripe Checkout Session for an invoice.

        Returns checkout session details including the URL to redirect the customer to.
        """
        cls._init_stripe()

        # Build line items from invoice
        line_items = []
        for item in invoice.line_items:
            line_items.append({
                'price_data': {
                    'currency': invoice.currency.lower(),
                    'unit_amount': int(item.unit_price * 100),  # Stripe uses cents
                    'product_data': {
                        'name': item.description,
                    },
                },
                'quantity': int(item.quantity),
            })

        # Add tax if applicable
        tax_behavior = 'exclusive'  # Tax calculated on top of subtotal

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                customer_email=invoice.client.email,
                metadata={
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'company_id': invoice.company_id
                },
                payment_intent_data={
                    'metadata': {
                        'invoice_id': invoice.id,
                        'invoice_number': invoice.invoice_number
                    }
                }
            )

            # Save checkout session ID to invoice
            invoice.payment_link = session.url
            db.session.commit()

            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'expires_at': datetime.fromtimestamp(session.expires_at).isoformat()
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe checkout session error: {str(e)}')
            raise

    @classmethod
    def create_payment_intent(cls, invoice: Invoice) -> dict:
        """
        Create a Stripe Payment Intent for an invoice.

        Use this for custom payment flows instead of Checkout.
        """
        cls._init_stripe()

        try:
            # Calculate amount in cents
            amount = int(invoice.balance_due * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=invoice.currency.lower(),
                metadata={
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'company_id': invoice.company_id
                },
                receipt_email=invoice.client.email,
                description=f'Payment for Invoice {invoice.invoice_number}'
            )

            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'currency': invoice.currency
            }

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe payment intent error: {str(e)}')
            raise

    @classmethod
    def retrieve_checkout_session(cls, session_id: str) -> dict:
        """Retrieve details of a checkout session"""
        cls._init_stripe()

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'id': session.id,
                'status': session.status,
                'payment_status': session.payment_status,
                'amount_total': session.amount_total,
                'currency': session.currency,
                'customer_email': session.customer_email,
                'metadata': session.metadata
            }
        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe session retrieve error: {str(e)}')
            raise

    @classmethod
    def retrieve_payment_intent(cls, payment_intent_id: str) -> dict:
        """Retrieve details of a payment intent"""
        cls._init_stripe()

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'id': intent.id,
                'status': intent.status,
                'amount': intent.amount,
                'amount_received': intent.amount_received,
                'currency': intent.currency,
                'metadata': intent.metadata
            }
        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe payment intent retrieve error: {str(e)}')
            raise

    @classmethod
    def handle_webhook_event(cls, payload: bytes, signature: str) -> dict:
        """
        Handle incoming Stripe webhook events.

        Returns the processed event details.
        """
        cls._init_stripe()
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

        if not webhook_secret:
            raise ValueError('STRIPE_WEBHOOK_SECRET not configured')

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except ValueError as e:
            raise ValueError(f'Invalid payload: {str(e)}')
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f'Invalid signature: {str(e)}')

        # Process the event
        event_type = event['type']
        event_data = event['data']['object']

        result = {
            'event_type': event_type,
            'event_id': event['id'],
            'processed': False,
            'message': ''
        }

        if event_type == 'checkout.session.completed':
            result = cls._handle_checkout_completed(event_data)
        elif event_type == 'payment_intent.succeeded':
            result = cls._handle_payment_succeeded(event_data)
        elif event_type == 'payment_intent.payment_failed':
            result = cls._handle_payment_failed(event_data)
        elif event_type == 'charge.refunded':
            result = cls._handle_refund(event_data)

        result['event_type'] = event_type
        result['event_id'] = event['id']

        return result

    @classmethod
    def _handle_checkout_completed(cls, session: dict) -> dict:
        """Handle successful checkout session"""
        invoice_id = session.get('metadata', {}).get('invoice_id')

        if not invoice_id:
            return {'processed': False, 'message': 'No invoice_id in metadata'}

        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return {'processed': False, 'message': f'Invoice {invoice_id} not found'}

        # Get payment amount
        amount = Decimal(session.get('amount_total', 0)) / 100

        # Record the payment
        payment = InvoicePayment(
            invoice_id=invoice.id,
            amount=amount,
            payment_method='card',
            stripe_payment_intent_id=session.get('payment_intent'),
            stripe_charge_id=session.get('payment_intent'),
            status='completed',
            payment_date=datetime.utcnow(),
            notes='Payment via Stripe Checkout'
        )
        db.session.add(payment)

        # Update invoice
        invoice.amount_paid = (invoice.amount_paid or 0) + amount
        invoice.balance_due = invoice.total - invoice.amount_paid
        invoice.stripe_invoice_id = session.get('payment_intent')

        if invoice.balance_due <= 0:
            invoice.status = Invoice.STATUS_PAID
            invoice.paid_at = datetime.utcnow()
        else:
            invoice.status = Invoice.STATUS_PARTIAL

        db.session.commit()

        return {
            'processed': True,
            'message': f'Payment of {amount} recorded for invoice {invoice.invoice_number}',
            'invoice_id': invoice.id,
            'amount_paid': float(amount)
        }

    @classmethod
    def _handle_payment_succeeded(cls, payment_intent: dict) -> dict:
        """Handle successful payment intent"""
        invoice_id = payment_intent.get('metadata', {}).get('invoice_id')

        if not invoice_id:
            return {'processed': False, 'message': 'No invoice_id in metadata'}

        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return {'processed': False, 'message': f'Invoice {invoice_id} not found'}

        # Check if payment already recorded
        existing_payment = InvoicePayment.query.filter_by(
            stripe_payment_intent_id=payment_intent.get('id')
        ).first()

        if existing_payment:
            return {'processed': True, 'message': 'Payment already recorded'}

        # Record the payment
        amount = Decimal(payment_intent.get('amount_received', 0)) / 100

        payment = InvoicePayment(
            invoice_id=invoice.id,
            amount=amount,
            payment_method='card',
            stripe_payment_intent_id=payment_intent.get('id'),
            status='completed',
            payment_date=datetime.utcnow(),
            notes='Payment via Stripe'
        )
        db.session.add(payment)

        # Update invoice
        invoice.amount_paid = (invoice.amount_paid or 0) + amount
        invoice.balance_due = invoice.total - invoice.amount_paid

        if invoice.balance_due <= 0:
            invoice.status = Invoice.STATUS_PAID
            invoice.paid_at = datetime.utcnow()
        else:
            invoice.status = Invoice.STATUS_PARTIAL

        db.session.commit()

        return {
            'processed': True,
            'message': f'Payment of {amount} recorded',
            'invoice_id': invoice.id,
            'amount_paid': float(amount)
        }

    @classmethod
    def _handle_payment_failed(cls, payment_intent: dict) -> dict:
        """Handle failed payment intent"""
        invoice_id = payment_intent.get('metadata', {}).get('invoice_id')

        if not invoice_id:
            return {'processed': False, 'message': 'No invoice_id in metadata'}

        # Log the failure but don't update invoice status
        current_app.logger.warning(
            f"Payment failed for invoice {invoice_id}: "
            f"{payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}"
        )

        return {
            'processed': True,
            'message': 'Payment failure logged',
            'invoice_id': invoice_id
        }

    @classmethod
    def _handle_refund(cls, charge: dict) -> dict:
        """Handle charge refund"""
        payment_intent_id = charge.get('payment_intent')

        if not payment_intent_id:
            return {'processed': False, 'message': 'No payment_intent in charge'}

        # Find the payment
        payment = InvoicePayment.query.filter_by(
            stripe_payment_intent_id=payment_intent_id
        ).first()

        if not payment:
            return {'processed': False, 'message': 'Payment not found'}

        # Update payment status
        refund_amount = Decimal(charge.get('amount_refunded', 0)) / 100
        payment.status = 'refunded'
        payment.refund_amount = refund_amount
        payment.refunded_at = datetime.utcnow()

        # Update invoice
        invoice = payment.invoice
        invoice.amount_paid = (invoice.amount_paid or 0) - refund_amount
        invoice.balance_due = invoice.total - invoice.amount_paid

        if invoice.amount_paid <= 0:
            invoice.status = Invoice.STATUS_SENT
            invoice.paid_at = None
        elif invoice.balance_due > 0:
            invoice.status = Invoice.STATUS_PARTIAL

        db.session.commit()

        return {
            'processed': True,
            'message': f'Refund of {refund_amount} processed',
            'invoice_id': invoice.id,
            'refund_amount': float(refund_amount)
        }

    @classmethod
    def create_customer(cls, user) -> str:
        """Create or retrieve a Stripe customer for a user"""
        cls._init_stripe()

        # Check if user already has a Stripe customer ID
        if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            return user.stripe_customer_id

        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    'user_id': user.id,
                    'company_id': user.company_id
                }
            )

            # Save customer ID to user (if field exists)
            if hasattr(user, 'stripe_customer_id'):
                user.stripe_customer_id = customer.id
                db.session.commit()

            return customer.id

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe customer creation error: {str(e)}')
            raise

    @classmethod
    def list_payment_methods(cls, customer_id: str) -> list:
        """List saved payment methods for a customer"""
        cls._init_stripe()

        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )

            return [
                {
                    'id': pm.id,
                    'type': pm.type,
                    'card': {
                        'brand': pm.card.brand,
                        'last4': pm.card.last4,
                        'exp_month': pm.card.exp_month,
                        'exp_year': pm.card.exp_year
                    }
                }
                for pm in payment_methods.data
            ]

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe list payment methods error: {str(e)}')
            raise

    @classmethod
    def get_public_key(cls) -> str:
        """Get the Stripe publishable key for frontend"""
        return current_app.config.get('STRIPE_PUBLISHABLE_KEY', '')
