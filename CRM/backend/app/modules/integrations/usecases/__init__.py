"""
Integration Use Cases

Business logic layer for integration operations.
"""

# Xero use cases
from .connect_xero import (
    ConnectXeroUseCase,
    DisconnectXeroUseCase,
    GetXeroStatusUseCase
)
from .sync_xero_contacts import (
    SyncXeroContactsUseCase,
    PushSingleContactToXeroUseCase
)
from .sync_xero_invoices import (
    SyncXeroInvoicesUseCase,
    PushSingleInvoiceToXeroUseCase,
    SyncXeroPaymentStatusUseCase
)

__all__ = [
    # Xero connection
    'ConnectXeroUseCase',
    'DisconnectXeroUseCase',
    'GetXeroStatusUseCase',

    # Xero contacts
    'SyncXeroContactsUseCase',
    'PushSingleContactToXeroUseCase',

    # Xero invoices
    'SyncXeroInvoicesUseCase',
    'PushSingleInvoiceToXeroUseCase',
    'SyncXeroPaymentStatusUseCase',
]
