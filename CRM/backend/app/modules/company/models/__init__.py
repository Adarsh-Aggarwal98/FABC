"""
Company Models
==============

This package contains all models for the company module.
All models are exported from this __init__.py for backward compatibility.
"""
from app.modules.company.models.enums import (
    ContactType,
    EmailProviderType,
    StorageProviderType
)
from app.modules.company.models.company import Company
from app.modules.company.models.currency import Currency
from app.modules.company.models.tax_type import TaxType
from app.modules.company.models.company_email_config import CompanyEmailConfig
from app.modules.company.models.company_storage_config import CompanyStorageConfig
from app.modules.company.models.system_email_config import SystemEmailConfig
from app.modules.company.models.company_contact import CompanyContact

__all__ = [
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
]
