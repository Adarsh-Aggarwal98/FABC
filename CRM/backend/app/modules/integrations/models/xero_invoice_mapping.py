"""
Xero Invoice Mapping Model

Maps CRM invoices to Xero invoices.
"""

from datetime import datetime


def create_xero_invoice_mapping_model(db):
    """
    Factory function to create XeroInvoiceMapping model.

    Args:
        db: SQLAlchemy database instance

    Returns:
        XeroInvoiceMapping model class
    """

    class XeroInvoiceMapping(db.Model):
        """
        Maps CRM invoices to Xero invoices.
        Tracks sync status for each invoice.
        """
        __tablename__ = 'xero_invoice_mappings'

        id = db.Column(db.Integer, primary_key=True)
        xero_connection_id = db.Column(db.String(36), db.ForeignKey('xero_connections.id', ondelete='CASCADE'), nullable=False)

        # CRM side
        crm_invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)

        # Xero side
        xero_invoice_id = db.Column(db.String(100), nullable=False)
        xero_invoice_number = db.Column(db.String(50))
        xero_invoice_status = db.Column(db.String(50))  # DRAFT, SUBMITTED, AUTHORISED, PAID, VOIDED

        # Sync tracking
        last_synced_at = db.Column(db.DateTime)
        sync_status = db.Column(db.String(20), default='synced')  # synced, pending, error
        sync_error = db.Column(db.Text)

        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        __table_args__ = (
            db.UniqueConstraint('xero_connection_id', 'crm_invoice_id', name='unique_crm_invoice'),
            db.UniqueConstraint('xero_connection_id', 'xero_invoice_id', name='unique_xero_invoice'),
        )

        def to_dict(self):
            return {
                'id': self.id,
                'xero_connection_id': self.xero_connection_id,
                'crm_invoice_id': self.crm_invoice_id,
                'xero_invoice_id': self.xero_invoice_id,
                'xero_invoice_number': self.xero_invoice_number,
                'xero_invoice_status': self.xero_invoice_status,
                'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
                'sync_status': self.sync_status,
                'sync_error': self.sync_error
            }

        def __repr__(self):
            return f'<XeroInvoiceMapping {self.xero_invoice_number}>'

    return XeroInvoiceMapping
