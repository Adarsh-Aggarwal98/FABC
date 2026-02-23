"""
InvoiceLineItem Model - Individual line item on an invoice
"""
from datetime import datetime
from app.extensions import db


class InvoiceLineItem(db.Model):
    """Individual line item on an invoice"""
    __tablename__ = 'invoice_line_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)

    # Item details
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    # Optional service link
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)

    # Display order
    order = db.Column(db.Integer, default=0)

    # Optional: Tax exemption for this item
    is_tax_exempt = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service = db.relationship('Service', backref='invoice_line_items')

    def calculate_total(self):
        """Calculate line item total"""
        self.total = self.quantity * self.unit_price

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 1,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total': float(self.total) if self.total else 0,
            'service_id': self.service_id,
            'is_tax_exempt': self.is_tax_exempt,
            'order': self.order
        }

    def __repr__(self):
        return f'<InvoiceLineItem {self.description[:30]}>'
