"""
Xero Integration Module (Backward Compatible)

This module maintains backward compatibility with existing code.
The actual implementation has been moved to the clean architecture structure.

Usage:
    from app.modules.integrations.xero import init_xero_routes, XeroConfig
    from app.extensions import db
    from flask_jwt_extended import jwt_required, get_jwt_identity

    xero_bp = init_xero_routes(db, jwt_required, get_jwt_identity)
    app.register_blueprint(xero_bp)
"""

# Import from new clean architecture locations
from ..services.xero_service import XeroConfig, XeroAuthClient, XeroAPIClient
from ..models import create_xero_models
from ..routes.xero_routes import xero_bp, init_xero_routes

# Backward compatibility - import the old sync service pattern
# This maintains compatibility with existing code that imports XeroSyncService
try:
    from .sync_service import XeroSyncService
except ImportError:
    # If old file doesn't exist, provide compatibility through new structure
    from ..usecases import (
        SyncXeroContactsUseCase,
        SyncXeroInvoicesUseCase,
        PushSingleContactToXeroUseCase,
        PushSingleInvoiceToXeroUseCase,
    )

    class XeroSyncService:
        """
        Compatibility wrapper for XeroSyncService.
        Delegates to new use case classes.
        """
        def __init__(self, db, xero_connection, models):
            self.db = db
            self.connection = xero_connection
            self.models = models

        def sync_contacts(self, user_id=None, is_manual=False):
            from ..repositories import XeroRepository
            from ..services import XeroAPIClient

            repository = XeroRepository(self.db, {
                'XeroConnection': self.models['XeroConnection'],
                'XeroContactMapping': self.models['XeroContactMapping'],
                'XeroInvoiceMapping': self.models['XeroInvoiceMapping'],
                'XeroSyncLog': self.models['XeroSyncLog']
            })
            api_client = XeroAPIClient(
                self.connection.access_token,
                self.connection.xero_tenant_id
            )
            use_case = SyncXeroContactsUseCase(
                repository, api_client, self.models['User']
            )
            return use_case.execute(
                self.connection.id,
                self.connection.company_id,
                user_id,
                is_manual
            )

        def sync_invoices(self, user_id=None, is_manual=False):
            from ..repositories import XeroRepository
            from ..services import XeroAPIClient

            repository = XeroRepository(self.db, {
                'XeroConnection': self.models['XeroConnection'],
                'XeroContactMapping': self.models['XeroContactMapping'],
                'XeroInvoiceMapping': self.models['XeroInvoiceMapping'],
                'XeroSyncLog': self.models['XeroSyncLog']
            })
            api_client = XeroAPIClient(
                self.connection.access_token,
                self.connection.xero_tenant_id
            )
            use_case = SyncXeroInvoicesUseCase(
                repository, api_client, self.models.get('Invoice'), self.connection
            )
            return use_case.execute(
                self.connection.company_id,
                user_id,
                is_manual
            )


__all__ = [
    'XeroConfig',
    'XeroAuthClient',
    'XeroAPIClient',
    'create_xero_models',
    'XeroSyncService',
    'init_xero_routes',
    'xero_bp'
]
