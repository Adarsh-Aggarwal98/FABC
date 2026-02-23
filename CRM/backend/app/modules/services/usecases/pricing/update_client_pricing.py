"""
Update Client Pricing Use Case
"""
from decimal import Decimal
from datetime import date

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import ClientServicePricing
from app.modules.user.models import User


class UpdateClientPricingUseCase(BaseCommandUseCase):
    """Update an existing client pricing record."""

    def execute(
        self,
        pricing_id: str,
        requester_id: str,
        custom_price: float = None,
        discount_percentage: float = None,
        notes: str = None,
        valid_from: str = None,
        valid_until: str = None,
        is_active: bool = None
    ) -> UseCaseResult:
        """
        Update a client pricing record.

        Args:
            pricing_id: ID of the pricing record to update
            requester_id: ID of the user making the update
            custom_price: New custom price (optional)
            discount_percentage: New discount percentage (optional)
            notes: Updated notes (optional)
            valid_from: New start date (optional)
            valid_until: New end date (optional)
            is_active: New active status (optional)

        Returns:
            UseCaseResult with updated pricing record
        """
        requester = User.query.get(requester_id)
        if not requester:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not requester.company_id:
            return UseCaseResult.fail('User has no company', 'NO_COMPANY')

        # Check permissions
        if requester.role.name not in ('super_admin', 'admin', 'senior_accountant'):
            return UseCaseResult.fail('Only admins can update client pricing', 'FORBIDDEN')

        pricing = ClientServicePricing.query.get(pricing_id)
        if not pricing:
            return UseCaseResult.fail('Pricing record not found', 'NOT_FOUND')

        # Ensure pricing belongs to requester's company
        if pricing.company_id != requester.company_id and requester.role.name != 'super_admin':
            return UseCaseResult.fail('Pricing record not found', 'NOT_FOUND')

        # Update fields if provided
        if custom_price is not None:
            pricing.custom_price = Decimal(str(custom_price)) if custom_price else None

        if discount_percentage is not None:
            if discount_percentage < 0 or discount_percentage > 100:
                return UseCaseResult.fail('Discount percentage must be between 0 and 100', 'INVALID_INPUT')
            pricing.discount_percentage = Decimal(str(discount_percentage)) if discount_percentage else None

        # Validate at least one pricing option remains
        if pricing.custom_price is None and pricing.discount_percentage is None:
            return UseCaseResult.fail('Either custom_price or discount_percentage is required', 'INVALID_INPUT')

        if notes is not None:
            pricing.notes = notes

        if valid_from is not None:
            try:
                pricing.valid_from = date.fromisoformat(valid_from) if valid_from else None
            except ValueError:
                return UseCaseResult.fail('Invalid valid_from date format', 'INVALID_INPUT')

        if valid_until is not None:
            try:
                pricing.valid_until = date.fromisoformat(valid_until) if valid_until else None
            except ValueError:
                return UseCaseResult.fail('Invalid valid_until date format', 'INVALID_INPUT')

        if is_active is not None:
            pricing.is_active = is_active

        pricing.updated_by_id = requester_id

        db.session.commit()

        return UseCaseResult.ok({
            'pricing': pricing.to_dict(include_service=True, include_client=True)
        })
