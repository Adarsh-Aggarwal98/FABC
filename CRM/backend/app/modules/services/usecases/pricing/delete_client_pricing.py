"""
Delete Client Pricing Use Case
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ClientServicePricing
from app.modules.user.models import User


class DeleteClientPricingUseCase(BaseCommandUseCase):
    """
    Delete (soft-delete) a client pricing record.

    Sets is_active=False rather than actually deleting.
    """

    def execute(self, pricing_id: str, requester_id: str) -> UseCaseResult:
        """
        Delete a client pricing record.

        Args:
            pricing_id: ID of the pricing record to delete
            requester_id: ID of the user making the request

        Returns:
            UseCaseResult with success status
        """
        requester = User.query.get(requester_id)
        if not requester:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not requester.company_id:
            return UseCaseResult.fail('User has no company', 'NO_COMPANY')

        # Check permissions
        if requester.role.name not in ('super_admin', 'admin', 'senior_accountant'):
            return UseCaseResult.fail('Only admins can delete client pricing', 'FORBIDDEN')

        pricing = ClientServicePricing.query.get(pricing_id)
        if not pricing:
            return UseCaseResult.fail('Pricing record not found', 'NOT_FOUND')

        # Ensure pricing belongs to requester's company
        if pricing.company_id != requester.company_id and requester.role.name != 'super_admin':
            return UseCaseResult.fail('Pricing record not found', 'NOT_FOUND')

        # Soft delete
        pricing.is_active = False
        pricing.updated_by_id = requester_id

        db.session.commit()

        return UseCaseResult.ok({
            'message': 'Pricing record deleted successfully'
        })
