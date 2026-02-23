"""
Search Repository - Data access layer for search operations

This module encapsulates all database queries for search functionality,
following the repository pattern to separate data access from business logic.
"""
from typing import List, Optional
from sqlalchemy import or_

from app.extensions import db


class SearchRepository:
    """Repository for search-related database operations"""

    @staticmethod
    def find_users(
        query: str = None,
        company_id: str = None,
        role_filter: str = None,
        tag_ids: List[int] = None,
        limit: int = 20
    ) -> List:
        """
        Find users matching search criteria.

        Args:
            query: Search string to match against name, email, phone
            company_id: Filter by company ID
            role_filter: Filter by role name
            tag_ids: Filter by tag IDs
            limit: Maximum number of results

        Returns:
            List of User model instances
        """
        from app.modules.user.models import User, Role
        from app.modules.tags.models import user_tags

        search_query = User.query

        if company_id:
            search_query = search_query.filter(User.company_id == company_id)

        if role_filter:
            search_query = search_query.join(Role).filter(Role.name == role_filter)

        if tag_ids:
            search_query = search_query.join(user_tags).filter(user_tags.c.tag_id.in_(tag_ids))

        if query:
            search_pattern = f'%{query}%'
            search_query = search_query.filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.phone.ilike(search_pattern),
                    User.company_name.ilike(search_pattern)
                )
            )

        return search_query.order_by(User.created_at.desc()).limit(limit).all()

    @staticmethod
    def find_requests(
        query: str = None,
        company_id: str = None,
        status: str = None,
        assigned_to: str = None,
        limit: int = 20
    ) -> List:
        """
        Find service requests matching search criteria.

        Args:
            query: Search string to match against service name, notes, user info
            company_id: Filter by company ID
            status: Filter by request status
            assigned_to: Filter by assigned accountant ID
            limit: Maximum number of results

        Returns:
            List of ServiceRequest model instances
        """
        from app.modules.services.models import ServiceRequest, Service
        from app.modules.user.models import User

        search_query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)

        if company_id:
            search_query = search_query.filter(User.company_id == company_id)

        if status:
            search_query = search_query.filter(ServiceRequest.status == status)

        if assigned_to:
            search_query = search_query.filter(ServiceRequest.assigned_accountant_id == assigned_to)

        if query:
            search_pattern = f'%{query}%'
            search_query = search_query.join(Service).filter(
                or_(
                    Service.name.ilike(search_pattern),
                    ServiceRequest.internal_notes.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern)
                )
            )

        return search_query.order_by(ServiceRequest.created_at.desc()).limit(limit).all()

    @staticmethod
    def find_documents(
        query: str = None,
        company_id: str = None,
        category: str = None,
        limit: int = 20
    ) -> List:
        """
        Find documents matching search criteria.

        Args:
            query: Search string to match against filename, description
            company_id: Filter by company ID
            category: Filter by document category
            limit: Maximum number of results

        Returns:
            List of Document model instances
        """
        from app.modules.documents.models import Document
        from app.modules.user.models import User

        search_query = Document.query.join(User, Document.uploaded_by_id == User.id)

        if company_id:
            search_query = search_query.filter(User.company_id == company_id)

        if category:
            search_query = search_query.filter(Document.category == category)

        if query:
            search_pattern = f'%{query}%'
            search_query = search_query.filter(
                or_(
                    Document.original_filename.ilike(search_pattern),
                    Document.description.ilike(search_pattern)
                )
            )

        return search_query.order_by(Document.created_at.desc()).limit(limit).all()
