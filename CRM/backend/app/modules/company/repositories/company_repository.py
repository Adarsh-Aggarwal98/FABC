"""
Company Repository - Data Access Layer
=======================================

Repository for Company entity with custom queries.
For simple CRUD, use the base methods from BaseRepository.
"""
from typing import Optional
from sqlalchemy import or_
from app.common.repository import BaseRepository
from app.modules.company.models import Company
from app.modules.user.models import User, Role


class CompanyRepository(BaseRepository[Company]):
    """Repository with custom Company queries"""
    model = Company

    def search(self, search_term: str, active_only: bool = True, page: int = 1, per_page: int = 20):
        """Search companies by name, trading name, email, or ABN"""
        query = Company.query
        if active_only:
            query = query.filter_by(is_active=True)
        if search_term:
            pattern = f'%{search_term}%'
            query = query.filter(or_(
                Company.name.ilike(pattern),
                Company.trading_name.ilike(pattern),
                Company.email.ilike(pattern),
                Company.abn.ilike(pattern)
            ))
        return query.order_by(Company.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_company_users(self, company_id: str, role_filter: str = None, page: int = 1, per_page: int = 20):
        """Get users belonging to a company with optional role filter"""
        query = User.query.filter_by(company_id=company_id, is_active=True)
        if role_filter:
            query = query.join(Role).filter(Role.name == role_filter)
        return query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def deactivate_company_users(self, company_id: str) -> int:
        """Deactivate all users in a company"""
        return User.query.filter_by(company_id=company_id).update({'is_active': False})
