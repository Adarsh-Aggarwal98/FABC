"""
List Default Services Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Service, CompanyServiceSettings
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository


class ListDefaultServicesUseCase(BaseQueryUseCase):
    """
    List all default services with company-specific activation status.

    Returns default services with their activation status for the practice.
    """

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str) -> UseCaseResult:
        """
        List default services with company activation status.

        Args:
            user_id: ID of the requesting user

        Returns:
            UseCaseResult with list of services
        """
        from app.modules.company.models import Company

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Get company type for filtering
        company_type = None
        if user.company_id:
            company = Company.query.get(user.company_id)
            if company:
                company_type = company.company_type

        # Build query for default services filtered by company type
        query = Service.query.filter_by(is_default=True, is_active=True)

        # Filter by company type (category) if set
        practice_owner_types = ['tax_agent', 'accountant', 'bas_agent', 'bookkeeper']

        if company_type:
            if company_type in practice_owner_types:
                # Practice owners can see all practice owner services
                query = query.filter(
                    db.or_(
                        Service.category.in_(practice_owner_types),
                        Service.category.is_(None),
                        Service.category == ''
                    )
                )
            else:
                # Other types see only their specific category
                query = query.filter(
                    db.or_(
                        Service.category == company_type,
                        Service.category.is_(None),
                        Service.category == ''
                    )
                )

        default_services = query.all()

        services_data = []
        for service in default_services:
            service_dict = service.to_dict(include_form=True, company_id=user.company_id)
            services_data.append(service_dict)

        return UseCaseResult.ok({
            'services': services_data,
            'total': len(services_data)
        })
