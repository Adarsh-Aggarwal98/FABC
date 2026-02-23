"""
List Services Use Case
"""
import logging
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Service
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository

logger = logging.getLogger(__name__)


class ListServicesUseCase(BaseQueryUseCase):
    """List all services (filtered by company type for non-super-admin users)"""

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, active_only: bool = True, category: str = None,
                user_id: str = None) -> UseCaseResult:
        """
        List services with optional filters.

        Args:
            active_only: Only return active services
            category: Filter by category
            user_id: User ID for role-based filtering

        Returns:
            UseCaseResult with list of services
        """
        from app.modules.company.models import Company

        # Get user and company type for filtering
        company_type = None
        is_super_admin = False
        is_client = False
        user = None

        if user_id:
            user = self.user_repo.get_by_id(user_id)
            if user:
                is_super_admin = user.role.name == 'super_admin'
                is_client = user.role.name == 'user'
                if user.company_id:
                    company = Company.query.get(user.company_id)
                    if company:
                        company_type = company.company_type

        logger.info(f"ListServices: user_id={user_id}, company_type={company_type}, is_super_admin={is_super_admin}, is_client={is_client}")

        # Super admins see all services
        if is_super_admin:
            services = self.service_repo.get_all_services(active_only, category)
            logger.info(f"Super admin: returning {len(services)} services")
        else:
            # Filter by company type
            query = Service.query
            if active_only:
                query = query.filter_by(is_active=True)
            if category:
                query = query.filter_by(category=category)

            # Filter by company type if set
            practice_owner_types = ['tax_agent', 'accountant', 'bas_agent', 'bookkeeper']

            if company_type:
                if company_type in practice_owner_types:
                    query = query.filter(
                        db.or_(
                            Service.category.in_(practice_owner_types),
                            Service.category.is_(None),
                            Service.category == ''
                        )
                    )
                else:
                    query = query.filter(
                        db.or_(
                            Service.category == company_type,
                            Service.category.is_(None),
                            Service.category == ''
                        )
                    )

            services = query.all()
            logger.info(f"Non-super admin: company_type={company_type}, returning {len(services)} services")

        # Convert services to dict, hiding prices for client users
        service_dicts = []
        for s in services:
            service_dict = s.to_dict(include_form=True)

            # Hide prices from client users - they should only see prices after invoice
            if is_client:
                service_dict['base_price'] = None
                if 'display_price' in service_dict:
                    service_dict['display_price'] = None

            service_dicts.append(service_dict)

        return UseCaseResult.ok({
            'services': service_dicts
        })
