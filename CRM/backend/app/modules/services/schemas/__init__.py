"""
Services Schemas Package

This module exports all schemas for the services module.
Import schemas from here for backward compatibility:
    from app.modules.services.schemas import CreateServiceSchema, CreateRequestSchema
"""

# Service Schemas
from .service_schemas import (
    ServiceSchema,
    CreateServiceSchema,
    UpdateServiceSchema,
)

# Request Schemas
from .request_schemas import (
    CreateRequestSchema,
    CreateMultipleRequestsSchema,
    AssignRequestSchema,
    UpdateStatusSchema,
    UpdateInvoiceSchema,
    UpdateCostSchema,
    AddNoteSchema,
    ServiceRequestListSchema,
)

# Query Schemas
from .query_schemas import (
    CreateQuerySchema,
    QuerySchema,
)

# Company Settings Schemas
from .company_settings_schemas import (
    CompanyServiceSettingsSchema,
    UpdateCompanyServiceSettingsSchema,
    ActivateServiceSchema,
    BulkServiceActivationSchema,
)

# Invoice Schemas
from .invoice_schemas import (
    InvoiceLineItemSchema,
    CreateInvoiceLineItemSchema,
    CreateInvoiceSchema,
    UpdateInvoiceDetailsSchema,
    AddInvoicePaymentSchema,
    SendInvoiceSchema,
    InvoiceSchema,
    InvoiceListSchema,
)

# Status Schemas
from .status_schemas import (
    StatusSchema,
    CreateStatusSchema as CreateCustomStatusSchema,
    UpdateStatusSchema as UpdateCustomStatusSchema,
    ReorderStatusesSchema,
    InitializeCustomStatusesSchema,
)

__all__ = [
    # Service
    'ServiceSchema',
    'CreateServiceSchema',
    'UpdateServiceSchema',
    # Request
    'CreateRequestSchema',
    'CreateMultipleRequestsSchema',
    'AssignRequestSchema',
    'UpdateStatusSchema',
    'UpdateInvoiceSchema',
    'UpdateCostSchema',
    'AddNoteSchema',
    'ServiceRequestListSchema',
    # Query
    'CreateQuerySchema',
    'QuerySchema',
    # Company Settings
    'CompanyServiceSettingsSchema',
    'UpdateCompanyServiceSettingsSchema',
    'ActivateServiceSchema',
    'BulkServiceActivationSchema',
    # Invoice
    'InvoiceLineItemSchema',
    'CreateInvoiceLineItemSchema',
    'CreateInvoiceSchema',
    'UpdateInvoiceDetailsSchema',
    'AddInvoicePaymentSchema',
    'SendInvoiceSchema',
    'InvoiceSchema',
    'InvoiceListSchema',
    # Status
    'StatusSchema',
    'CreateCustomStatusSchema',
    'UpdateCustomStatusSchema',
    'ReorderStatusesSchema',
    'InitializeCustomStatusesSchema',
]
