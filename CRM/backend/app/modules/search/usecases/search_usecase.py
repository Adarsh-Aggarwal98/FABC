"""
Search Use Cases - Business logic layer for search operations

This module contains the business logic for search functionality,
orchestrating repository calls and transforming data for the presentation layer.
"""
from typing import List, Dict, Any, Optional

from ..repositories.search_repository import SearchRepository


class SearchUseCase:
    """Use case class for search operations"""

    def __init__(self, repository: SearchRepository = None):
        """
        Initialize the use case with a repository.

        Args:
            repository: SearchRepository instance (defaults to new instance)
        """
        self.repository = repository or SearchRepository()

    def search_users(
        self,
        query: str = None,
        company_id: str = None,
        role_filter: str = None,
        tag_ids: List[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search users by name, email, phone with optional filters.

        Args:
            query: Search string
            company_id: Filter by company
            role_filter: Filter by role name
            tag_ids: Filter by tag IDs
            limit: Maximum results

        Returns:
            List of user dictionaries
        """
        users = self.repository.find_users(
            query=query,
            company_id=company_id,
            role_filter=role_filter,
            tag_ids=tag_ids,
            limit=limit
        )
        return [u.to_dict() for u in users]

    def search_requests(
        self,
        query: str = None,
        company_id: str = None,
        status: str = None,
        assigned_to: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search service requests with optional filters.

        Args:
            query: Search string
            company_id: Filter by company
            status: Filter by request status
            assigned_to: Filter by assigned accountant ID
            limit: Maximum results

        Returns:
            List of service request dictionaries
        """
        requests = self.repository.find_requests(
            query=query,
            company_id=company_id,
            status=status,
            assigned_to=assigned_to,
            limit=limit
        )
        return [r.to_dict() for r in requests]

    def search_documents(
        self,
        query: str = None,
        company_id: str = None,
        category: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search documents by name, description with optional filters.

        Args:
            query: Search string
            company_id: Filter by company
            category: Filter by document category
            limit: Maximum results

        Returns:
            List of document dictionaries
        """
        documents = self.repository.find_documents(
            query=query,
            company_id=company_id,
            category=category,
            limit=limit
        )
        return [d.to_dict() for d in documents]

    def search_all(
        self,
        query: str,
        company_id: str = None,
        limit_per_type: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all entity types.

        Args:
            query: Search string
            company_id: Filter by company
            limit_per_type: Maximum results per entity type

        Returns:
            Dictionary with 'users', 'requests', 'documents' keys
        """
        return {
            'users': self.search_users(query, company_id, limit=limit_per_type),
            'requests': self.search_requests(query, company_id, limit=limit_per_type),
            'documents': self.search_documents(query, company_id, limit=limit_per_type)
        }


# Default instance for backward compatibility
_default_use_case = None


def get_search_usecase() -> SearchUseCase:
    """Get the default SearchUseCase instance (singleton pattern)."""
    global _default_use_case
    if _default_use_case is None:
        _default_use_case = SearchUseCase()
    return _default_use_case
