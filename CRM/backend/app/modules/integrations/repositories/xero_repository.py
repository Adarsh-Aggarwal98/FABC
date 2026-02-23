"""
Xero Repository

Data access layer for Xero integration entities.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class XeroRepository:
    """
    Repository for Xero data access operations.
    Provides a clean interface for database operations.
    """

    def __init__(self, db, models: Dict):
        """
        Initialize repository with database and models.

        Args:
            db: SQLAlchemy database instance
            models: Dictionary containing model classes:
                {
                    'XeroConnection': XeroConnection,
                    'XeroContactMapping': XeroContactMapping,
                    'XeroInvoiceMapping': XeroInvoiceMapping,
                    'XeroSyncLog': XeroSyncLog
                }
        """
        self.db = db
        self.XeroConnection = models['XeroConnection']
        self.XeroContactMapping = models['XeroContactMapping']
        self.XeroInvoiceMapping = models['XeroInvoiceMapping']
        self.XeroSyncLog = models['XeroSyncLog']

    # ============== Connection Methods ==============

    def get_connection_by_company(self, company_id: str) -> Optional[Any]:
        """Get Xero connection for a company."""
        return self.XeroConnection.query.filter_by(company_id=company_id).first()

    def get_active_connection_by_company(self, company_id: str) -> Optional[Any]:
        """Get active Xero connection for a company."""
        return self.XeroConnection.query.filter_by(
            company_id=company_id,
            is_active=True
        ).first()

    def create_connection(self, **kwargs) -> Any:
        """Create a new Xero connection."""
        connection = self.XeroConnection(**kwargs)
        self.db.session.add(connection)
        self.db.session.flush()
        return connection

    def update_connection(self, connection, **kwargs) -> Any:
        """Update an existing connection."""
        for key, value in kwargs.items():
            if hasattr(connection, key):
                setattr(connection, key, value)
        connection.updated_at = datetime.utcnow()
        return connection

    def disconnect(self, connection) -> None:
        """Mark connection as disconnected."""
        connection.is_active = False
        connection.disconnected_at = datetime.utcnow()

    # ============== Contact Mapping Methods ==============

    def get_contact_mapping_by_user(self, connection_id: str, user_id: str) -> Optional[Any]:
        """Get contact mapping for a CRM user."""
        return self.XeroContactMapping.query.filter_by(
            xero_connection_id=connection_id,
            crm_user_id=user_id
        ).first()

    def get_contact_mapping_by_company(self, connection_id: str, company_id: str) -> Optional[Any]:
        """Get contact mapping for a CRM company."""
        return self.XeroContactMapping.query.filter_by(
            xero_connection_id=connection_id,
            crm_company_id=company_id
        ).first()

    def get_contact_mapping_by_xero_id(self, connection_id: str, xero_contact_id: str) -> Optional[Any]:
        """Get contact mapping by Xero contact ID."""
        return self.XeroContactMapping.query.filter_by(
            xero_connection_id=connection_id,
            xero_contact_id=xero_contact_id
        ).first()

    def get_all_contact_mappings(self, connection_id: str) -> List[Any]:
        """Get all contact mappings for a connection."""
        return self.XeroContactMapping.query.filter_by(
            xero_connection_id=connection_id,
            is_active=True
        ).all()

    def create_contact_mapping(self, **kwargs) -> Any:
        """Create a new contact mapping."""
        mapping = self.XeroContactMapping(**kwargs)
        self.db.session.add(mapping)
        self.db.session.flush()
        return mapping

    def update_contact_mapping(self, mapping, **kwargs) -> Any:
        """Update a contact mapping."""
        for key, value in kwargs.items():
            if hasattr(mapping, key):
                setattr(mapping, key, value)
        mapping.updated_at = datetime.utcnow()
        return mapping

    # ============== Invoice Mapping Methods ==============

    def get_invoice_mapping_by_crm_id(self, connection_id: str, crm_invoice_id: str) -> Optional[Any]:
        """Get invoice mapping by CRM invoice ID."""
        return self.XeroInvoiceMapping.query.filter_by(
            xero_connection_id=connection_id,
            crm_invoice_id=crm_invoice_id
        ).first()

    def get_invoice_mapping_by_xero_id(self, connection_id: str, xero_invoice_id: str) -> Optional[Any]:
        """Get invoice mapping by Xero invoice ID."""
        return self.XeroInvoiceMapping.query.filter_by(
            xero_connection_id=connection_id,
            xero_invoice_id=xero_invoice_id
        ).first()

    def get_all_invoice_mappings(self, connection_id: str) -> List[Any]:
        """Get all invoice mappings for a connection."""
        return self.XeroInvoiceMapping.query.filter_by(
            xero_connection_id=connection_id
        ).all()

    def create_invoice_mapping(self, **kwargs) -> Any:
        """Create a new invoice mapping."""
        mapping = self.XeroInvoiceMapping(**kwargs)
        self.db.session.add(mapping)
        self.db.session.flush()
        return mapping

    def update_invoice_mapping(self, mapping, **kwargs) -> Any:
        """Update an invoice mapping."""
        for key, value in kwargs.items():
            if hasattr(mapping, key):
                setattr(mapping, key, value)
        mapping.updated_at = datetime.utcnow()
        return mapping

    # ============== Sync Log Methods ==============

    def create_sync_log(self, connection_id: str, sync_type: str, direction: str,
                        user_id: str = None, is_manual: bool = False) -> Any:
        """Create a new sync log entry."""
        log = self.XeroSyncLog(
            xero_connection_id=connection_id,
            sync_type=sync_type,
            direction=direction,
            status='started',
            triggered_by_id=user_id,
            is_manual=is_manual
        )
        self.db.session.add(log)
        self.db.session.flush()
        return log

    def get_sync_logs(self, connection_id: str, page: int = 1, per_page: int = 20) -> Any:
        """Get paginated sync logs for a connection."""
        return self.XeroSyncLog.query.filter_by(
            xero_connection_id=connection_id
        ).order_by(
            self.XeroSyncLog.started_at.desc()
        ).paginate(page=page, per_page=per_page)

    def get_last_sync_log(self, connection_id: str) -> Optional[Any]:
        """Get the most recent sync log."""
        return self.XeroSyncLog.query.filter_by(
            xero_connection_id=connection_id
        ).order_by(
            self.XeroSyncLog.started_at.desc()
        ).first()

    # ============== Transaction Methods ==============

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.session.rollback()

    def flush(self) -> None:
        """Flush pending changes."""
        self.db.session.flush()
