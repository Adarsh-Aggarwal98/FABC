"""
Get Effective Price Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.models import Service
from app.modules.services.services import PricingService
from app.modules.user.models import User


class GetEffectivePriceUseCase(BaseQueryUseCase):
    """
    Get the effective price for a service for a specific client.

    This use case is accessible to all authenticated users, but:
    - Clients can only see prices after an invoice is raised
    - Staff can see suggested prices when creating invoices
    """

    def execute(
        self,
        service_id: int,
        requester_id: str,
        user_id: str = None,
        client_entity_id: str = None
    ) -> UseCaseResult:
        """
        Get the effective price for a service.

        Args:
            service_id: ID of the service
            requester_id: ID of the user making the request
            user_id: Optional user ID to get price for
            client_entity_id: Optional entity ID to get price for

        Returns:
            UseCaseResult with price info
        """
        requester = User.query.get(requester_id)
        if not requester:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        service = Service.query.get(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        is_staff = requester.role.name in ('super_admin', 'admin', 'senior_accountant', 'accountant')

        # For non-staff (clients), don't reveal pricing
        if not is_staff:
            return UseCaseResult.fail('Price information not available', 'FORBIDDEN')

        # Get effective price using PricingService
        price_info = PricingService.get_effective_price(
            service_id=service_id,
            user_id=user_id,
            client_entity_id=client_entity_id,
            company_id=requester.company_id
        )

        return UseCaseResult.ok({
            'service_id': service_id,
            'service_name': service.name,
            'base_price': float(service.base_price) if service.base_price else None,
            'effective_price': price_info['price'],
            'price_source': price_info['source'],
            'has_custom_pricing': price_info['source'] in ('entity_pricing', 'user_pricing'),
            'discount_percentage': price_info['discount_percentage'],
            'pricing_notes': price_info['notes']
        })
