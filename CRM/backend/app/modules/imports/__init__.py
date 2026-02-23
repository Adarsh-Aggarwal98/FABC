"""
Data Import Module

This module provides functionality for bulk importing data from CSV files.
Supports importing clients, service requests, services catalog, and companies.

Clean Architecture Structure:
----------------------------
- models/: Data models (ImportTemplate, ImportResult, etc.)
- repositories/: Data access layer (UserImportRepository, etc.)
- schemas/: Template definitions and validation schemas
- usecases/: Business logic (ImportClientsUseCase, etc.)
- routes/: HTTP controllers (thin layer)

Backward Compatibility:
----------------------
This module re-exports all necessary components for backward compatibility.
The Blueprint can be imported directly from this module or from routes/.
"""
# Re-export models
from app.modules.imports.models import (
    ImportTemplate,
    ImportType,
    ImportResult,
    ImportError,
    ImportedUser,
    ImportedServiceRequest,
    ImportedCompany
)

# Re-export repositories
from app.modules.imports.repositories import (
    UserImportRepository,
    ServiceImportRepository,
    CompanyImportRepository
)

# Re-export schemas
from app.modules.imports.schemas import (
    get_clients_template,
    get_service_requests_template,
    get_services_template,
    get_companies_template,
    get_template,
    get_available_template_types,
    get_all_import_types,
    VALID_SERVICE_REQUEST_STATUSES,
    VALID_PRIORITIES
)

# Re-export use cases
from app.modules.imports.usecases import (
    GetTemplateUseCase,
    ImportClientsUseCase,
    ImportServiceRequestsUseCase,
    ImportServicesUseCase,
    ImportCompaniesUseCase,
    GetAvailableTypesUseCase
)

# Re-export Blueprint for backward compatibility
from app.modules.imports.routes import import_bp

__all__ = [
    # Models
    'ImportTemplate',
    'ImportType',
    'ImportResult',
    'ImportError',
    'ImportedUser',
    'ImportedServiceRequest',
    'ImportedCompany',
    # Repositories
    'UserImportRepository',
    'ServiceImportRepository',
    'CompanyImportRepository',
    # Schemas
    'get_clients_template',
    'get_service_requests_template',
    'get_services_template',
    'get_companies_template',
    'get_template',
    'get_available_template_types',
    'get_all_import_types',
    'VALID_SERVICE_REQUEST_STATUSES',
    'VALID_PRIORITIES',
    # Use cases
    'GetTemplateUseCase',
    'ImportClientsUseCase',
    'ImportServiceRequestsUseCase',
    'ImportServicesUseCase',
    'ImportCompaniesUseCase',
    'GetAvailableTypesUseCase',
    # Blueprint
    'import_bp'
]
