"""
Xero Connection Model

Stores OAuth connection details for Xero integration.
"""

import uuid
from datetime import datetime, timedelta


def create_xero_connection_model(db):
    """
    Factory function to create XeroConnection model.

    Args:
        db: SQLAlchemy database instance

    Returns:
        XeroConnection model class
    """

    class XeroConnection(db.Model):
        """
        Stores Xero OAuth connection for a company.
        Each company can have one active Xero connection.
        """
        __tablename__ = 'xero_connections'

        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True)

        # Xero tenant (organization) info
        xero_tenant_id = db.Column(db.String(100), nullable=False)
        xero_tenant_name = db.Column(db.String(200))
        xero_tenant_type = db.Column(db.String(50))  # COMPANY, PRACTICE, etc.

        # OAuth tokens (encrypted in production)
        access_token = db.Column(db.Text, nullable=False)
        refresh_token = db.Column(db.Text, nullable=False)
        token_expires_at = db.Column(db.DateTime, nullable=False)

        # Token scopes granted
        scopes = db.Column(db.Text)  # Space-separated scopes

        # Connection status
        is_active = db.Column(db.Boolean, default=True)
        last_sync_at = db.Column(db.DateTime)
        last_error = db.Column(db.Text)

        # Sync settings
        auto_sync_contacts = db.Column(db.Boolean, default=True)
        auto_sync_invoices = db.Column(db.Boolean, default=True)
        sync_interval_minutes = db.Column(db.Integer, default=60)

        # Default account mappings
        default_sales_account_id = db.Column(db.String(100))  # Xero account for sales/revenue
        default_bank_account_id = db.Column(db.String(100))  # Xero bank account for payments

        # Audit fields
        connected_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
        connected_at = db.Column(db.DateTime, default=datetime.utcnow)
        disconnected_at = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def is_token_expired(self) -> bool:
            """Check if access token is expired or about to expire (5 min buffer)"""
            if not self.token_expires_at:
                return True
            return datetime.utcnow() >= (self.token_expires_at - timedelta(minutes=5))

        def update_tokens(self, access_token: str, refresh_token: str, expires_in: int, scopes: str = None):
            """Update OAuth tokens"""
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            if scopes:
                self.scopes = scopes
            self.updated_at = datetime.utcnow()

        def to_dict(self, include_tokens: bool = False):
            data = {
                'id': self.id,
                'company_id': self.company_id,
                'xero_tenant_id': self.xero_tenant_id,
                'xero_tenant_name': self.xero_tenant_name,
                'xero_tenant_type': self.xero_tenant_type,
                'is_active': self.is_active,
                'is_token_expired': self.is_token_expired(),
                'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
                'last_error': self.last_error,
                'auto_sync_contacts': self.auto_sync_contacts,
                'auto_sync_invoices': self.auto_sync_invoices,
                'sync_interval_minutes': self.sync_interval_minutes,
                'connected_at': self.connected_at.isoformat() if self.connected_at else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            if include_tokens:
                data['token_expires_at'] = self.token_expires_at.isoformat() if self.token_expires_at else None
            return data

        def __repr__(self):
            return f'<XeroConnection {self.xero_tenant_name}>'

    return XeroConnection
