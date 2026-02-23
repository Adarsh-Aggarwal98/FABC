"""
Invoice Model - Invoice for billing clients
"""
import uuid
from datetime import datetime
from app.extensions import db


class Invoice(db.Model):
    """
    Invoice model for billing clients.

    Supports:
    - Multiple line items per invoice
    - Tax calculations (GST for Australian accounting)
    - Multiple payment tracking
    - Link to service requests
    - Draft/Sent/Paid workflow
    """
    __tablename__ = 'invoices'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Invoice identification
    invoice_number = db.Column(db.String(50), nullable=False, unique=True)
    reference = db.Column(db.String(100))  # Optional reference/PO number

    # Company (issuer)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=False)

    # Client (recipient)
    client_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Linked service request (optional - invoice may be for multiple or none)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id'), nullable=True)

    # Dates
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)

    # Financial
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=10)  # Default 10% GST for Australia
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_description = db.Column(db.String(200))
    total = db.Column(db.Numeric(10, 2), default=0)
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    balance_due = db.Column(db.Numeric(10, 2), default=0)

    # Currency (default AUD)
    currency = db.Column(db.String(3), default='AUD')

    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, viewed, partial, paid, overdue, cancelled

    # Notes
    notes = db.Column(db.Text)  # Visible to client
    internal_notes = db.Column(db.Text)  # Internal only

    # Payment terms
    payment_terms = db.Column(db.Text)

    # Payment link (Stripe, etc.)
    payment_link = db.Column(db.String(500))
    stripe_invoice_id = db.Column(db.String(100))

    # Tracking
    sent_at = db.Column(db.DateTime)
    viewed_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Relationships
    company = db.relationship('Company', backref=db.backref('invoices', lazy='dynamic'))
    client = db.relationship('User', foreign_keys=[client_id], backref=db.backref('invoices_received', lazy='dynamic'))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='invoices_created')
    service_request = db.relationship('ServiceRequest', backref=db.backref('invoices', lazy='dynamic'))
    line_items = db.relationship('InvoiceLineItem', backref='invoice', lazy='dynamic',
                                  cascade='all, delete-orphan', order_by='InvoiceLineItem.order')
    payments = db.relationship('InvoicePayment', backref='invoice', lazy='dynamic',
                               cascade='all, delete-orphan', order_by='InvoicePayment.payment_date.desc()')

    # Status constants
    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_VIEWED = 'viewed'
    STATUS_PARTIAL = 'partial'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'
    STATUS_CANCELLED = 'cancelled'

    VALID_STATUSES = [STATUS_DRAFT, STATUS_SENT, STATUS_VIEWED, STATUS_PARTIAL,
                      STATUS_PAID, STATUS_OVERDUE, STATUS_CANCELLED]

    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        self.subtotal = sum(item.total for item in self.line_items)
        self.tax_amount = (self.subtotal - self.discount_amount) * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount - self.discount_amount
        self.balance_due = self.total - self.amount_paid

        # Update status based on payments
        if self.balance_due <= 0 and self.total > 0:
            self.status = self.STATUS_PAID
            if not self.paid_at:
                self.paid_at = datetime.utcnow()
        elif self.amount_paid > 0:
            self.status = self.STATUS_PARTIAL

    def add_payment(self, amount, method='card', reference=None, notes=None):
        """Add a payment to this invoice"""
        from .invoice_payment import InvoicePayment

        payment = InvoicePayment(
            invoice_id=self.id,
            amount=amount,
            payment_method=method,
            reference=reference,
            notes=notes
        )
        db.session.add(payment)
        self.amount_paid = (self.amount_paid or 0) + amount
        self.calculate_totals()
        return payment

    @staticmethod
    def generate_invoice_number(company_id):
        """Generate a unique invoice number for a company.

        Uses global counter across all companies to ensure uniqueness
        since invoice_number has a global UNIQUE constraint.
        Format: INV-YYYY-NNNNN
        """
        from datetime import datetime
        year = datetime.utcnow().year

        # Get count of ALL invoices this year (globally unique)
        count = Invoice.query.filter(
            db.extract('year', Invoice.created_at) == year
        ).count()

        return f"INV-{year}-{str(count + 1).zfill(5)}"

    def to_dict(self, include_items=True, include_payments=False, include_client=True):
        data = {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'reference': self.reference,
            'company_id': self.company_id,
            'service_request_id': self.service_request_id,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'discount_description': self.discount_description,
            'total': float(self.total) if self.total else 0,
            'amount_paid': float(self.amount_paid) if self.amount_paid else 0,
            'balance_due': float(self.balance_due) if self.balance_due else 0,
            'currency': self.currency,
            'status': self.status,
            'notes': self.notes,
            'payment_terms': self.payment_terms,
            'payment_link': self.payment_link,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_client and self.client:
            data['client'] = {
                'id': self.client.id,
                'email': self.client.email,
                'full_name': self.client.full_name,
                'company_name': self.client.company_name,
                'address': self.client.address
            }

        if include_items:
            data['line_items'] = [item.to_dict() for item in self.line_items]
            data['item_count'] = self.line_items.count()

        if include_payments:
            data['payments'] = [p.to_dict() for p in self.payments]

        return data

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
