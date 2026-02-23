"""
Get Client Pricing Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.models import ClientServicePricing
from app.modules.user.models import User


class GetClientPricingUseCase(BaseQueryUseCase):
    """Get a specific client pricing record by ID."""

    def execute(self, pricing_id: str, requester_id: str) -> UseCaseResult:
        """
        Get a client pricing record.

        Args:
            pricing_id: ID of the pricing record
            requester_id: ID of the user making the request

        Returns:
            UseCaseResult with pricing record
        """
        requester = User.query.get(requester_id)
        if not requester:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not requester.company_id:
            return UseCaseResult.fail('User has no company', 'NO_COMPANY')

        # Check permissions
        if requester.role.name not in ('super_admin', 'admin', 'senior_accountant'):
            return UseCaseResult.fail('Only admins can view client pricing', 'FORBIDDEN')

        pricing = ClientServicePricing.query.get(pricing_id)
        if not pricing:
            return UseCaseResult.fail('Pricing record not found', 'NOT_FOUND')

        # Ensure pricing belongs to requester's company
        if pricing.company_id != requester.company_id and requester.role.name != 'super_admin':
            return UseCaseResult.fail('Pricing record not found', 'NOT_FOUND')

        return UseCaseResult.ok({
            'pricing': pricing.to_dict(include_service=True, include_client=True)
        })
