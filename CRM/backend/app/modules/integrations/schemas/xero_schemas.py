"""
Xero Schemas

Pydantic/Marshmallow schemas for Xero integration data validation.
"""

from typing import Optional, List
from datetime import datetime


# ============== Request Schemas ==============

class XeroConnectRequest:
    """Request to initiate Xero connection"""
    pass  # No body needed, uses session state


class XeroDisconnectRequest:
    """Request to disconnect from Xero"""
    pass  # No body needed


class XeroSyncRequest:
    """Request to sync data with Xero"""
    def __init__(self, direction: str = 'bidirectional'):
        self.direction = direction  # push, pull, bidirectional


class XeroSettingsUpdateRequest:
    """Request to update Xero settings"""
    def __init__(
        self,
        auto_sync_contacts: Optional[bool] = None,
        auto_sync_invoices: Optional[bool] = None,
        sync_interval_minutes: Optional[int] = None,
        default_sales_account_id: Optional[str] = None,
        default_bank_account_id: Optional[str] = None
    ):
        self.auto_sync_contacts = auto_sync_contacts
        self.auto_sync_invoices = auto_sync_invoices
        self.sync_interval_minutes = sync_interval_minutes
        self.default_sales_account_id = default_sales_account_id
        self.default_bank_account_id = default_bank_account_id


# ============== Response Schemas ==============

class XeroConnectionResponse:
    """Xero connection details response"""
    def __init__(
        self,
        id: str,
        company_id: str,
        xero_tenant_id: str,
        xero_tenant_name: Optional[str],
        is_active: bool,
        last_sync_at: Optional[datetime],
        auto_sync_contacts: bool,
        auto_sync_invoices: bool,
        connected_at: Optional[datetime]
    ):
        self.id = id
        self.company_id = company_id
        self.xero_tenant_id = xero_tenant_id
        self.xero_tenant_name = xero_tenant_name
        self.is_active = is_active
        self.last_sync_at = last_sync_at
        self.auto_sync_contacts = auto_sync_contacts
        self.auto_sync_invoices = auto_sync_invoices
        self.connected_at = connected_at


class XeroStatusResponse:
    """Xero connection status response"""
    def __init__(
        self,
        connected: bool,
        connection: Optional[dict] = None,
        last_sync: Optional[dict] = None,
        message: Optional[str] = None
    ):
        self.connected = connected
        self.connection = connection
        self.last_sync = last_sync
        self.message = message


class XeroSyncResultResponse:
    """Xero sync operation result"""
    def __init__(
        self,
        success: bool,
        sync_log_id: Optional[int] = None,
        processed: int = 0,
        created: int = 0,
        updated: int = 0,
        failed: int = 0,
        errors: Optional[List[str]] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.sync_log_id = sync_log_id
        self.processed = processed
        self.created = created
        self.updated = updated
        self.failed = failed
        self.errors = errors or []
        self.error = error


class XeroSyncLogResponse:
    """Xero sync log entry"""
    def __init__(
        self,
        id: int,
        sync_type: str,
        direction: str,
        status: str,
        records_processed: int,
        records_created: int,
        records_updated: int,
        records_failed: int,
        started_at: Optional[datetime],
        completed_at: Optional[datetime],
        duration_seconds: Optional[int],
        is_manual: bool
    ):
        self.id = id
        self.sync_type = sync_type
        self.direction = direction
        self.status = status
        self.records_processed = records_processed
        self.records_created = records_created
        self.records_updated = records_updated
        self.records_failed = records_failed
        self.started_at = started_at
        self.completed_at = completed_at
        self.duration_seconds = duration_seconds
        self.is_manual = is_manual


class XeroContactMappingResponse:
    """Xero contact mapping details"""
    def __init__(
        self,
        id: int,
        crm_user_id: Optional[str],
        crm_company_id: Optional[str],
        xero_contact_id: str,
        xero_contact_name: Optional[str],
        last_synced_at: Optional[datetime],
        sync_direction: str,
        is_active: bool
    ):
        self.id = id
        self.crm_user_id = crm_user_id
        self.crm_company_id = crm_company_id
        self.xero_contact_id = xero_contact_id
        self.xero_contact_name = xero_contact_name
        self.last_synced_at = last_synced_at
        self.sync_direction = sync_direction
        self.is_active = is_active


class XeroInvoiceMappingResponse:
    """Xero invoice mapping details"""
    def __init__(
        self,
        id: int,
        crm_invoice_id: str,
        xero_invoice_id: str,
        xero_invoice_number: Optional[str],
        xero_invoice_status: Optional[str],
        last_synced_at: Optional[datetime],
        sync_status: str,
        sync_error: Optional[str]
    ):
        self.id = id
        self.crm_invoice_id = crm_invoice_id
        self.xero_invoice_id = xero_invoice_id
        self.xero_invoice_number = xero_invoice_number
        self.xero_invoice_status = xero_invoice_status
        self.last_synced_at = last_synced_at
        self.sync_status = sync_status
        self.sync_error = sync_error


# ============== Utility Functions ==============

def success_response(data, message: str = None, status_code: int = 200):
    """Create a standard success response"""
    response = {'success': True, 'data': data}
    if message:
        response['message'] = message
    return response, status_code


def error_response(error: str, status_code: int = 400):
    """Create a standard error response"""
    return {'success': False, 'error': error}, status_code
