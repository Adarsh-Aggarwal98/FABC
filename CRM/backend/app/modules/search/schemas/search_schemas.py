"""
Search Schemas - Request/Response validation schemas

This module defines Pydantic-style or dataclass schemas for validating
search API requests and responses.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class GlobalSearchRequest:
    """Schema for global search request parameters"""
    query: str
    search_type: str = 'all'  # all, users, requests, documents
    limit: int = 10
    company_id: Optional[str] = None

    def validate(self) -> Optional[str]:
        """
        Validate the search request.

        Returns:
            Error message if invalid, None if valid
        """
        if not self.query:
            return 'Search query is required'
        if self.search_type not in ('all', 'users', 'requests', 'documents'):
            return 'Invalid search type'
        if self.limit < 1 or self.limit > 100:
            return 'Limit must be between 1 and 100'
        return None


@dataclass
class UserSearchRequest:
    """Schema for user search request parameters"""
    query: str = ''
    role_filter: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    limit: int = 20
    company_id: Optional[str] = None

    @classmethod
    def from_request_args(cls, args: dict, company_id: str = None) -> 'UserSearchRequest':
        """
        Create a UserSearchRequest from Flask request args.

        Args:
            args: Request arguments dictionary
            company_id: Company ID for scoping

        Returns:
            UserSearchRequest instance
        """
        tag_ids = None
        tags_str = args.get('tags', '')
        if tags_str:
            try:
                tag_ids = [int(t.strip()) for t in tags_str.split(',') if t.strip()]
            except ValueError:
                tag_ids = None  # Will be handled as validation error

        return cls(
            query=args.get('q', ''),
            role_filter=args.get('role'),
            tag_ids=tag_ids,
            limit=args.get('limit', 20, type=int) if hasattr(args, 'get') else int(args.get('limit', 20)),
            company_id=company_id
        )


@dataclass
class RequestSearchRequest:
    """Schema for service request search parameters"""
    query: str = ''
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    limit: int = 20
    company_id: Optional[str] = None

    @classmethod
    def from_request_args(cls, args: dict, company_id: str = None) -> 'RequestSearchRequest':
        """
        Create a RequestSearchRequest from Flask request args.

        Args:
            args: Request arguments dictionary
            company_id: Company ID for scoping

        Returns:
            RequestSearchRequest instance
        """
        return cls(
            query=args.get('q', ''),
            status=args.get('status'),
            assigned_to=args.get('assigned_to'),
            limit=args.get('limit', 20, type=int) if hasattr(args, 'get') else int(args.get('limit', 20)),
            company_id=company_id
        )


@dataclass
class SearchResult:
    """Schema for a single search result"""
    id: str
    type: str  # user, request, document
    title: str
    subtitle: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    """Schema for search response"""
    users: List[Dict[str, Any]] = field(default_factory=list)
    requests: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            'users': self.users,
            'requests': self.requests,
            'documents': self.documents
        }
