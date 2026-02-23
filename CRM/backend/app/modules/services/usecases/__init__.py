"""
Services Use Cases Package

This module exports all use cases for the services module.
Import use cases from here for backward compatibility:
    from app.modules.services.usecases import CreateServiceUseCase, ListServicesUseCase
"""

# Service Catalog Use Cases
from .services import (
    CreateServiceUseCase,
    UpdateServiceUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
)

# Service Request Use Cases
from .requests import (
    CreateServiceRequestUseCase,
    CreateMultipleRequestsUseCase,
    GetServiceRequestUseCase,
    ListServiceRequestsUseCase,
    AssignRequestUseCase,
    UpdateRequestStatusUseCase,
    UpdateInvoiceUseCase,
    AddInternalNoteUseCase,
    UpdateRequestUseCase,
    ReassignRequestUseCase,
    UpdateCostUseCase,
)

# Query Use Cases
from .queries import (
    CreateQueryUseCase,
    GetQueriesUseCase,
)

# Dashboard Use Cases
from .dashboard import (
    GetDashboardMetricsUseCase,
)

# Company Service Settings Use Cases
from .company_settings import (
    ListDefaultServicesUseCase,
    GetCompanyServiceSettingsUseCase,
    ActivateServiceForCompanyUseCase,
    UpdateCompanyServiceSettingsUseCase,
    BulkActivateServicesUseCase,
    ListServicesForCompanyUseCase,
)

# Invoice Use Cases
from .invoices import (
    CreateInvoiceUseCase,
    UpdateInvoiceDetailsUseCase,
    AddInvoiceLineItemUseCase,
    RemoveInvoiceLineItemUseCase,
    SendInvoiceUseCase,
    AddInvoicePaymentUseCase,
    GetInvoiceUseCase,
    ListInvoicesUseCase,
    CancelInvoiceUseCase,
)

# Status Use Cases
from .status import (
    GetStatusesUseCase,
    GetSystemStatusesUseCase,
    InitializeCustomStatusesUseCase,
    CreateCustomStatusUseCase,
    UpdateCustomStatusUseCase,
    DeleteCustomStatusUseCase,
    ReorderStatusesUseCase,
    ResetToSystemDefaultsUseCase,
    GetStatusForRequestUseCase,
)

# Client Pricing Use Cases
from .pricing import (
    ListClientPricingUseCase,
    GetClientPricingUseCase,
    CreateClientPricingUseCase,
    UpdateClientPricingUseCase,
    DeleteClientPricingUseCase,
    GetEffectivePriceUseCase,
)

__all__ = [
    # Service Catalog
    'CreateServiceUseCase',
    'UpdateServiceUseCase',
    'GetServiceUseCase',
    'ListServicesUseCase',
    # Service Requests
    'CreateServiceRequestUseCase',
    'CreateMultipleRequestsUseCase',
    'GetServiceRequestUseCase',
    'ListServiceRequestsUseCase',
    'AssignRequestUseCase',
    'UpdateRequestStatusUseCase',
    'UpdateInvoiceUseCase',
    'AddInternalNoteUseCase',
    'UpdateRequestUseCase',
    'ReassignRequestUseCase',
    'UpdateCostUseCase',
    # Queries
    'CreateQueryUseCase',
    'GetQueriesUseCase',
    # Dashboard
    'GetDashboardMetricsUseCase',
    # Company Settings
    'ListDefaultServicesUseCase',
    'GetCompanyServiceSettingsUseCase',
    'ActivateServiceForCompanyUseCase',
    'UpdateCompanyServiceSettingsUseCase',
    'BulkActivateServicesUseCase',
    'ListServicesForCompanyUseCase',
    # Invoices
    'CreateInvoiceUseCase',
    'UpdateInvoiceDetailsUseCase',
    'AddInvoiceLineItemUseCase',
    'RemoveInvoiceLineItemUseCase',
    'SendInvoiceUseCase',
    'AddInvoicePaymentUseCase',
    'GetInvoiceUseCase',
    'ListInvoicesUseCase',
    'CancelInvoiceUseCase',
    # Status
    'GetStatusesUseCase',
    'GetSystemStatusesUseCase',
    'InitializeCustomStatusesUseCase',
    'CreateCustomStatusUseCase',
    'UpdateCustomStatusUseCase',
    'DeleteCustomStatusUseCase',
    'ReorderStatusesUseCase',
    'ResetToSystemDefaultsUseCase',
    'GetStatusForRequestUseCase',
    # Client Pricing
    'ListClientPricingUseCase',
    'GetClientPricingUseCase',
    'CreateClientPricingUseCase',
    'UpdateClientPricingUseCase',
    'DeleteClientPricingUseCase',
    'GetEffectivePriceUseCase',
]
