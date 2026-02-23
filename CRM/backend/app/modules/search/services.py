"""
Search module services - Global search across entities

DEPRECATED: This module is maintained for backward compatibility.
New code should use SearchUseCase from search.usecases instead.
"""
from typing import List, Dict, Any

from .usecases.search_usecase import SearchUseCase


class SearchService:
    """
    Service for searching across multiple entities.

    DEPRECATED: This class delegates to SearchUseCase.
    New code should use SearchUseCase directly.
    """

    _use_case = SearchUseCase()

    @staticmethod
    def search_users(
        query: str,
        company_id: str = None,
        role_filter: str = None,
        tag_ids: List[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search users by name, email, phone"""
        return SearchService._use_case.search_users(
            query=query,
            company_id=company_id,
            role_filter=role_filter,
            tag_ids=tag_ids,
            limit=limit
        )

    @staticmethod
    def search_requests(
        query: str,
        company_id: str = None,
        status: str = None,
        assigned_to: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search service requests"""
        return SearchService._use_case.search_requests(
            query=query,
            company_id=company_id,
            status=status,
            assigned_to=assigned_to,
            limit=limit
        )

    @staticmethod
    def search_documents(
        query: str,
        company_id: str = None,
        category: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search documents by name, description"""
        return SearchService._use_case.search_documents(
            query=query,
            company_id=company_id,
            category=category,
            limit=limit
        )

    @staticmethod
    def search_all(
        query: str,
        company_id: str = None,
        limit_per_type: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all entity types"""
        return SearchService._use_case.search_all(
            query=query,
            company_id=company_id,
            limit_per_type=limit_per_type
        )
