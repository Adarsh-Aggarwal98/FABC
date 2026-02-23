"""
Company Repositories
====================

This package contains all repositories for the company module.
All repositories are exported from this __init__.py for backward compatibility.
"""
from app.modules.company.repositories.company_repository import CompanyRepository
from app.modules.company.repositories.user_repository import UserRepository
from app.modules.company.repositories.role_repository import RoleRepository

__all__ = [
    'CompanyRepository',
    'UserRepository',
    'RoleRepository',
]
