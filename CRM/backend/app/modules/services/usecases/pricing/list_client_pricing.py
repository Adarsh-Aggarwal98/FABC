"""
List Client Pricing Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.models import ClientServicePricing
from app.modules.user.models import User


class ListClientPricingUseCase(BaseQueryUseCase):
    """
    List all client pricing records for a company.

    Can filter by:
    - user_id: Get pricing for a specific user
    - client_entity_id: Get pricing for a specific entity
    - service_id: Get pricing for a specific service
    """

    def execute(
        self,
        requester_id: str,
        user_id: str = None,
        client_entity_id: str = None,
        service_id: int = None,
        include_inactive: bool = False
    ) -> UseCaseResult:
        """
        List client pricing records.

        Args:
            requester_id: ID of the user making the request (for auth)
            user_id: Optional filter by user
            client_entity_id: Optional filter by client entity
            service_id: Optional filter by service
            include_inactive: Whether to include inactive pricing

        Returns:
            UseCaseResult with list of pricing records
        """
        requester = User.query.get(requester_id)
        if not requester:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not requester.company_id:
            return UseCaseResult.fail('User has no company', 'NO_COMPANY')

        # Check permissions - only admin/senior roles can view pricing
        if requester.role.name not in ('super_admin', 'admin', 'senior_accountant'):
            return UseCaseResult.fail('Only admins can view client pricing', 'FORBIDDEN')

        query = ClientServicePricing.query.filter_by(company_id=requester.company_id)

        if user_id:
            query = query.filter_by(user_id=user_id)

        if client_entity_id:
            query = query.filter_by(client_entity_id=client_entity_id)

        if service_id:
            query = query.filter_by(service_id=service_id)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        pricing_records = query.order_by(ClientServicePricing.created_at.desc()).all()

        return UseCaseResult.ok({
            'pricing': [p.to_dict(include_service=True, include_client=True) for p in pricing_records],
            'count': len(pricing_records)
        })
