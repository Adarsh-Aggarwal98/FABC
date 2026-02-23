"""
Company Repositories (Backward Compatibility)
==============================================

This module re-exports all repositories from the repositories/ package for backward compatibility.
New code should import directly from:
    from app.modules.company.repositories import CompanyRepository, UserRepository, RoleRepository

Or from individual files:
    from app.modules.company.repositories.company_repository import CompanyRepository
"""
# Re-export everything from the repositories package
from app.modules.company.repositories import (
    CompanyRepository,
    UserRepository,
    RoleRepository,
)

__all__ = [
    'CompanyRepository',
    'UserRepository',
    'RoleRepository',
]
