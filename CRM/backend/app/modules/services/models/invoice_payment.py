"""
InvoicePayment Model - Payment record for an invoice
"""
from datetime import datetime
from app.extensions import db


class InvoicePayment(db.Model):
    """Payment record for an invoice"""
    __tablename__ = 'invoice_payments'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)

    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), default='card')  # card, bank_transfer, cash, cheque, other
    reference = db.Column(db.String(100))  # Transaction ID, cheque number, etc.
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, refunded

    # Stripe integration
    stripe_payment_id = db.Column(db.String(100))
    stripe_payment_intent_id = db.Column(db.String(100))
    stripe_charge_id = db.Column(db.String(100))

    # Refund tracking
    refund_amount = db.Column(db.Numeric(10, 2))
    refunded_at = db.Column(db.DateTime)

    # Timestamps
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Payment method constants
    METHOD_CARD = 'card'
    METHOD_BANK_TRANSFER = 'bank_transfer'
    METHOD_CASH = 'cash'
    METHOD_CHEQUE = 'cheque'
    METHOD_OTHER = 'other'

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'amount': float(self.amount) if self.amount else 0,
            'payment_method': self.payment_method,
            'reference': self.reference,
            'notes': self.notes,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<InvoicePayment {self.amount} for invoice {self.invoice_id}>'
