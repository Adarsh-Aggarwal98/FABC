"""
Company Module
==============

This module handles company/practice management including:
- Company CRUD operations
- Company settings (email, storage, currency)
- Company contacts
- Plan/subscription management

Clean Architecture Structure:
-----------------------------
- models/: Database models (Company, Currency, TaxType, etc.)
- repositories/: Data access layer
- usecases/: Business logic layer
- routes/: API endpoints (thin controllers)
- schemas/: Request/response schemas (for future use)
- services.py: Domain services (PlanLimitService, CompanyService)

Backward Compatibility:
----------------------
All models, repositories, and use cases are re-exported at module level
for backward compatibility with existing imports.
"""
from flask import Blueprint

# Create the blueprint
company_bp = Blueprint('company', __name__, url_prefix='/api/companies')

# Import routes (this registers routes on company_bp)
from app.modules.company.routes import company_routes

# Re-export models for backward compatibility
from app.modules.company.models import (
    # Enums
    ContactType,
    EmailProviderType,
    StorageProviderType,
    # Models
    Company,
    Currency,
    TaxType,
    CompanyEmailConfig,
    CompanyStorageConfig,
    SystemEmailConfig,
    CompanyContact,
)

# Re-export repositories for backward compatibility
from app.modules.company.repositories import (
    CompanyRepository,
    UserRepository,
    RoleRepository,
)

# Re-export use cases for backward compatibility
from app.modules.company.usecases import (
    CreateCompanyUseCase,
    UpdateCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    DeleteCompanyUseCase,
    AddUserToCompanyUseCase,
    GetCompanyUsersUseCase,
    TransferOwnershipUseCase,
    GetMyCompanyUseCase,
    ListCompanyContactsUseCase,
    GetCompanyContactHistoryUseCase,
    AddCompanyContactUseCase,
    UpdateCompanyContactUseCase,
    DeleteCompanyContactUseCase,
    SetPrimaryContactUseCase,
)

__all__ = [
    # Blueprint
    'company_bp',
    # Enums
    'ContactType',
    'EmailProviderType',
    'StorageProviderType',
    # Models
    'Company',
    'Currency',
    'TaxType',
    'CompanyEmailConfig',
    'CompanyStorageConfig',
    'SystemEmailConfig',
    'CompanyContact',
    # Repositories
    'CompanyRepository',
    'UserRepository',
    'RoleRepository',
    # Use Cases
    'CreateCompanyUseCase',
    'UpdateCompanyUseCase',
    'GetCompanyUseCase',
    'ListCompaniesUseCase',
    'DeleteCompanyUseCase',
    'AddUserToCompanyUseCase',
    'GetCompanyUsersUseCase',
    'TransferOwnershipUseCase',
    'GetMyCompanyUseCase',
    'ListCompanyContactsUseCase',
    'GetCompanyContactHistoryUseCase',
    'AddCompanyContactUseCase',
    'UpdateCompanyContactUseCase',
    'DeleteCompanyContactUseCase',
    'SetPrimaryContactUseCase',
]
