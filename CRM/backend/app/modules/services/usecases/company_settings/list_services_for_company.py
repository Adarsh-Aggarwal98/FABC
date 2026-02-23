"""
List Services for Company Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Service, CompanyServiceSettings
from app.modules.services.repositories import ServiceRepository
from app.modules.user.repositories import UserRepository


class ListServicesForCompanyUseCase(BaseQueryUseCase):
    """
    List services available to a company's clients.

    Returns only active services (respecting company-level activation).
    Filters by company type (category) when applicable.
    """

    def __init__(self):
        self.service_repo = ServiceRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str, include_inactive: bool = False) -> UseCaseResult:
        """
        List services available to a company.

        Args:
            user_id: ID of the requesting user
            include_inactive: Whether to include inactive services

        Returns:
            UseCaseResult with list of services
        """
        from app.modules.company.models import Company

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        company_id = user.company_id
        company_type = None

        # Get company type for filtering
        if company_id:
            company = Company.query.get(company_id)
            if company:
                company_type = company.company_type

        # Build base query
        if include_inactive:
            query = Service.query
        else:
            query = Service.query.filter_by(is_active=True)

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

        services = query.all()

        services_data = []
        for service in services:
            # Check company-level activation for default services
            if service.is_default and company_id:
                settings = CompanyServiceSettings.query.filter_by(
                    company_id=company_id,
                    service_id=service.id
                ).first()

                # If settings exist and service is deactivated, skip (unless include_inactive)
                if settings and not settings.is_active and not include_inactive:
                    continue

            service_dict = service.to_dict(include_form=True, company_id=company_id)
            services_data.append(service_dict)

        return UseCaseResult.ok({
            'services': services_data,
            'total': len(services_data)
        })
