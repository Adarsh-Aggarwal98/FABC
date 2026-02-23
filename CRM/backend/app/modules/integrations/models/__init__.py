"""
Integration Models

Re-exports all integration models for backward compatibility.
Each model is split into its own file following clean architecture.
"""

from .xero_connection import create_xero_connection_model
from .xero_contact_mapping import create_xero_contact_mapping_model
from .xero_invoice_mapping import create_xero_invoice_mapping_model
from .xero_sync_log import create_xero_sync_log_model


def create_xero_models(db):
    """
    Factory function to create all Xero models with the given db instance.
    Maintains backward compatibility with existing code.

    Usage:
        from app.extensions import db
        from app.modules.integrations.models import create_xero_models

        XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = create_xero_models(db)
    """
    XeroConnection = create_xero_connection_model(db)
    XeroContactMapping = create_xero_contact_mapping_model(db)
    XeroInvoiceMapping = create_xero_invoice_mapping_model(db)
    XeroSyncLog = create_xero_sync_log_model(db)

    return XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog


__all__ = [
    # Xero model factories
    'create_xero_connection_model',
    'create_xero_contact_mapping_model',
    'create_xero_invoice_mapping_model',
    'create_xero_sync_log_model',
    'create_xero_models',
]
