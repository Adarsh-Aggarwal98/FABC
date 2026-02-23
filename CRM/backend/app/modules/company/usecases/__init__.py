"""
Company Use Cases
=================

This package contains all use cases for the company module.
All use cases are exported from this __init__.py for backward compatibility.
"""
from app.modules.company.usecases.company_usecases import (
    # Company Use Cases
    CreateCompanyUseCase,
    UpdateCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    DeleteCompanyUseCase,
    # User Management Use Cases
    AddUserToCompanyUseCase,
    GetCompanyUsersUseCase,
    TransferOwnershipUseCase,
    GetMyCompanyUseCase,
    # Contact Use Cases
    ListCompanyContactsUseCase,
    GetCompanyContactHistoryUseCase,
    AddCompanyContactUseCase,
    UpdateCompanyContactUseCase,
    DeleteCompanyContactUseCase,
    SetPrimaryContactUseCase,
)

__all__ = [
    # Company Use Cases
    'CreateCompanyUseCase',
    'UpdateCompanyUseCase',
    'GetCompanyUseCase',
    'ListCompaniesUseCase',
    'DeleteCompanyUseCase',
    # User Management Use Cases
    'AddUserToCompanyUseCase',
    'GetCompanyUsersUseCase',
    'TransferOwnershipUseCase',
    'GetMyCompanyUseCase',
    # Contact Use Cases
    'ListCompanyContactsUseCase',
    'GetCompanyContactHistoryUseCase',
    'AddCompanyContactUseCase',
    'UpdateCompanyContactUseCase',
    'DeleteCompanyContactUseCase',
    'SetPrimaryContactUseCase',
]
