"""
Company Models (Backward Compatibility)
=======================================

This module re-exports all models from the models/ package for backward compatibility.
New code should import directly from:
    from app.modules.company.models import Company, Currency, etc.

Or from individual files:
    from app.modules.company.models.company import Company
"""
# Re-export everything from the models package
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

__all__ = [
    'ContactType',
    'EmailProviderType',
    'StorageProviderType',
    'Company',
    'Currency',
    'TaxType',
    'CompanyEmailConfig',
    'CompanyStorageConfig',
    'SystemEmailConfig',
    'CompanyContact',
]
