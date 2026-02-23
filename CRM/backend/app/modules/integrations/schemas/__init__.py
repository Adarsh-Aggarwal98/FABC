"""
Integration Schemas

Data validation schemas for integration APIs.
"""

from .xero_schemas import (
    XeroConnectRequest,
    XeroDisconnectRequest,
    XeroSyncRequest,
    XeroSettingsUpdateRequest,
    XeroConnectionResponse,
    XeroStatusResponse,
    XeroSyncResultResponse,
    XeroSyncLogResponse,
    XeroContactMappingResponse,
    XeroInvoiceMappingResponse,
    success_response,
    error_response
)

__all__ = [
    # Xero request schemas
    'XeroConnectRequest',
    'XeroDisconnectRequest',
    'XeroSyncRequest',
    'XeroSettingsUpdateRequest',

    # Xero response schemas
    'XeroConnectionResponse',
    'XeroStatusResponse',
    'XeroSyncResultResponse',
    'XeroSyncLogResponse',
    'XeroContactMappingResponse',
    'XeroInvoiceMappingResponse',

    # Utility functions
    'success_response',
    'error_response',
]
