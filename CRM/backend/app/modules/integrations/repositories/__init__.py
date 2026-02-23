"""
Integration Repositories

Re-exports all repository classes for data access.
"""

from .xero_repository import XeroRepository

__all__ = [
    'XeroRepository',
]
