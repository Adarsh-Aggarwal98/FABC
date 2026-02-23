"""
Company Use Cases (Backward Compatibility)
==========================================

This module re-exports all use cases from the usecases/ package for backward compatibility.
New code should import directly from:
    from app.modules.company.usecases import CreateCompanyUseCase, etc.

Or from individual files:
    from app.modules.company.usecases.company_usecases import CreateCompanyUseCase
"""
# Re-export everything from the usecases package
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
