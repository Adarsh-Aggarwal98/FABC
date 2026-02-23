"""
Xero Integration Models

Standalone models for Xero integration.
These models need to be registered with SQLAlchemy separately.

To register, add to your app initialization:
    from app.modules.integrations.xero.models import XeroConnection, XeroContactMapping, XeroInvoiceMapping
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional


def create_xero_models(db):
    """
    Factory function to create Xero models with the given db instance.
    This avoids circular imports and allows the models to be optional.

    Usage:
        from app.extensions import db
        from app.modules.integrations.xero.models import create_xero_models

        XeroConnection, XeroContactMapping, XeroInvoiceMapping = create_xero_models(db)
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


    class XeroContactMapping(db.Model):
        """
        Maps CRM users/companies to Xero contacts.
        Allows bidirectional sync between systems.
        """
        __tablename__ = 'xero_contact_mappings'

        id = db.Column(db.Integer, primary_key=True)
        xero_connection_id = db.Column(db.String(36), db.ForeignKey('xero_connections.id', ondelete='CASCADE'), nullable=False)

        # CRM side - either a user or company
        crm_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
        crm_company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

        # Xero side
        xero_contact_id = db.Column(db.String(100), nullable=False)
        xero_contact_name = db.Column(db.String(200))

        # Sync tracking
        last_synced_at = db.Column(db.DateTime)
        sync_direction = db.Column(db.String(20), default='bidirectional')  # crm_to_xero, xero_to_crm, bidirectional
        is_active = db.Column(db.Boolean, default=True)

        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        __table_args__ = (
            db.UniqueConstraint('xero_connection_id', 'xero_contact_id', name='unique_xero_contact'),
            db.UniqueConstraint('xero_connection_id', 'crm_user_id', name='unique_crm_user_contact'),
            db.UniqueConstraint('xero_connection_id', 'crm_company_id', name='unique_crm_company_contact'),
        )

        def to_dict(self):
            return {
                'id': self.id,
                'xero_connection_id': self.xero_connection_id,
                'crm_user_id': self.crm_user_id,
                'crm_company_id': self.crm_company_id,
                'xero_contact_id': self.xero_contact_id,
                'xero_contact_name': self.xero_contact_name,
                'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
                'sync_direction': self.sync_direction,
                'is_active': self.is_active
            }

        def __repr__(self):
            return f'<XeroContactMapping {self.xero_contact_name}>'


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


    class XeroSyncLog(db.Model):
        """
        Logs all sync operations for debugging and auditing.
        """
        __tablename__ = 'xero_sync_logs'

        id = db.Column(db.Integer, primary_key=True)
        xero_connection_id = db.Column(db.String(36), db.ForeignKey('xero_connections.id', ondelete='CASCADE'), nullable=False)

        # Sync details
        sync_type = db.Column(db.String(50), nullable=False)  # contacts, invoices, payments, full
        direction = db.Column(db.String(20), nullable=False)  # push, pull, bidirectional
        status = db.Column(db.String(20), nullable=False)  # started, completed, failed

        # Results
        records_processed = db.Column(db.Integer, default=0)
        records_created = db.Column(db.Integer, default=0)
        records_updated = db.Column(db.Integer, default=0)
        records_failed = db.Column(db.Integer, default=0)
        error_details = db.Column(db.JSON)

        # Timing
        started_at = db.Column(db.DateTime, default=datetime.utcnow)
        completed_at = db.Column(db.DateTime)
        duration_seconds = db.Column(db.Integer)

        # Who triggered it
        triggered_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
        is_manual = db.Column(db.Boolean, default=False)  # Manual vs automatic sync

        def complete(self, status: str = 'completed'):
            self.status = status
            self.completed_at = datetime.utcnow()
            if self.started_at:
                self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

        def to_dict(self):
            return {
                'id': self.id,
                'xero_connection_id': self.xero_connection_id,
                'sync_type': self.sync_type,
                'direction': self.direction,
                'status': self.status,
                'records_processed': self.records_processed,
                'records_created': self.records_created,
                'records_updated': self.records_updated,
                'records_failed': self.records_failed,
                'error_details': self.error_details,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'duration_seconds': self.duration_seconds,
                'is_manual': self.is_manual
            }

        def __repr__(self):
            return f'<XeroSyncLog {self.sync_type} {self.status}>'

    return XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog
