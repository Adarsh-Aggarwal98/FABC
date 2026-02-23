"""
User Repository - Data access for User entity
"""
from typing import Optional, List
from sqlalchemy import or_
from app.common.repository import BaseRepository
from app.modules.user.models import User, Role


class UserRepository(BaseRepository[User]):
    """Repository for User data access"""
    model = User

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return User.query.filter_by(email=email.lower().strip()).first()

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return User.query.filter_by(email=email.lower().strip()).first() is not None

    def get_users_paginated(self, role_filter: str = None, page: int = 1, per_page: int = 20, company_id: str = None, name_search: str = None):
        """Get paginated list of users with optional role, company, and name filter"""
        query = User.query

        if role_filter:
            role = Role.query.filter_by(name=role_filter).first()
            if role:
                query = query.filter_by(role_id=role.id)

        if company_id:
            query = query.filter_by(company_id=company_id)

        # Name search filter - searches first_name, last_name, and email
        if name_search:
            search_term = f'%{name_search}%'
            query = query.filter(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )

        query = query.order_by(User.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_accountants(self, company_id: str = None, include_senior: bool = True) -> List[User]:
        """Get all active accountants and optionally senior accountants, filtered by company"""
        roles_to_include = [Role.ACCOUNTANT]
        if include_senior:
            roles_to_include.append(Role.SENIOR_ACCOUNTANT)

        roles = Role.query.filter(Role.name.in_(roles_to_include)).all()
        if not roles:
            return []

        role_ids = [r.id for r in roles]
        query = User.query.filter(
            User.role_id.in_(role_ids),
            User.is_active == True
        )

        if company_id:
            query = query.filter_by(company_id=company_id)

        return query.all()

    def get_senior_accountants(self, company_id: str = None) -> List[User]:
        """Get all active senior accountants, optionally filtered by company"""
        senior_role = Role.query.filter_by(name=Role.SENIOR_ACCOUNTANT).first()
        if not senior_role:
            return []

        query = User.query.filter_by(
            role_id=senior_role.id,
            is_active=True
        )

        if company_id:
            query = query.filter_by(company_id=company_id)

        return query.all()

    def get_supervised_accountants(self, supervisor_id: str) -> List[User]:
        """Get all accountants supervised by a specific senior accountant"""
        return User.query.filter_by(
            supervisor_id=supervisor_id,
            is_active=True
        ).all()

    def get_by_company(self, company_id: str, active_only: bool = True) -> List[User]:
        """Get all users belonging to a company"""
        query = User.query.filter_by(company_id=company_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
