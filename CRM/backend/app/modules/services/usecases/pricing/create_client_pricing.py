"""
Create Client Pricing Use Case
"""
from decimal import Decimal
from datetime import datetime

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.services.models import Service, ClientServicePricing
from app.modules.user.models import User
from app.modules.client_entity.models import ClientEntity


class CreateClientPricingUseCase(BaseCommandUseCase):
    """
    Create a new client-specific pricing record.

    Business Rules:
    - Either user_id OR client_entity_id must be provided (not both)
    - Either custom_price OR discount_percentage must be provided
    - Service must exist
    - User/Entity must exist and belong to the same company
    - Cannot create duplicate active pricing for same client+service
    """

    def execute(
        self,
        requester_id: str,
        service_id: int,
        user_id: str = None,
        client_entity_id: str = None,
        custom_price: float = None,
        discount_percentage: float = None,
        notes: str = None,
        valid_from: str = None,
        valid_until: str = None
    ) -> UseCaseResult:
        """
        Create a client pricing record.

        Args:
            requester_id: ID of the user creating the record
            service_id: ID of the service
            user_id: ID of the user client (optional)
            client_entity_id: ID of the client entity (optional)
            custom_price: Fixed custom price (optional)
            discount_percentage: Discount percentage (optional)
            notes: Additional notes (optional)
            valid_from: Start date for pricing (optional)
            valid_until: End date for pricing (optional)

        Returns:
            UseCaseResult with created pricing record
        """
        requester = User.query.get(requester_id)
        if not requester:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not requester.company_id:
            return UseCaseResult.fail('User has no company', 'NO_COMPANY')

        # Check permissions
        if requester.role.name not in ('super_admin', 'admin', 'senior_accountant'):
            return UseCaseResult.fail('Only admins can create client pricing', 'FORBIDDEN')

        # Validate client reference
        if not user_id and not client_entity_id:
            return UseCaseResult.fail('Either user_id or client_entity_id is required', 'INVALID_INPUT')

        if user_id and client_entity_id:
            return UseCaseResult.fail('Cannot specify both user_id and client_entity_id', 'INVALID_INPUT')

        # Validate pricing option
        if custom_price is None and discount_percentage is None:
            return UseCaseResult.fail('Either custom_price or discount_percentage is required', 'INVALID_INPUT')

        # Validate service exists
        service = Service.query.get(service_id)
        if not service:
            return UseCaseResult.fail('Service not found', 'NOT_FOUND')

        # Validate user/entity exists and belongs to company
        if user_id:
            client_user = User.query.get(user_id)
            if not client_user:
                return UseCaseResult.fail('Client user not found', 'NOT_FOUND')
            if client_user.company_id != requester.company_id and requester.role.name != 'super_admin':
                return UseCaseResult.fail('Client does not belong to your company', 'FORBIDDEN')

            # Check for existing active pricing
            existing = ClientServicePricing.query.filter_by(
                user_id=user_id,
                service_id=service_id,
                is_active=True
            ).first()
            if existing:
                return UseCaseResult.fail('Active pricing already exists for this client and service', 'DUPLICATE')

        if client_entity_id:
            entity = ClientEntity.query.get(client_entity_id)
            if not entity:
                return UseCaseResult.fail('Client entity not found', 'NOT_FOUND')
            if entity.company_id != requester.company_id and requester.role.name != 'super_admin':
                return UseCaseResult.fail('Client entity does not belong to your company', 'FORBIDDEN')

            # Check for existing active pricing
            existing = ClientServicePricing.query.filter_by(
                client_entity_id=client_entity_id,
                service_id=service_id,
                is_active=True
            ).first()
            if existing:
                return UseCaseResult.fail('Active pricing already exists for this entity and service', 'DUPLICATE')

        # Parse dates if provided
        from datetime import date
        parsed_valid_from = None
        parsed_valid_until = None

        if valid_from:
            try:
                parsed_valid_from = date.fromisoformat(valid_from)
            except ValueError:
                return UseCaseResult.fail('Invalid valid_from date format', 'INVALID_INPUT')

        if valid_until:
            try:
                parsed_valid_until = date.fromisoformat(valid_until)
            except ValueError:
                return UseCaseResult.fail('Invalid valid_until date format', 'INVALID_INPUT')

        # Validate discount percentage range
        if discount_percentage is not None:
            if discount_percentage < 0 or discount_percentage > 100:
                return UseCaseResult.fail('Discount percentage must be between 0 and 100', 'INVALID_INPUT')

        # Create pricing record
        pricing = ClientServicePricing(
            company_id=requester.company_id,
            user_id=user_id,
            client_entity_id=client_entity_id,
            service_id=service_id,
            custom_price=Decimal(str(custom_price)) if custom_price is not None else None,
            discount_percentage=Decimal(str(discount_percentage)) if discount_percentage is not None else None,
            notes=notes,
            valid_from=parsed_valid_from,
            valid_until=parsed_valid_until,
            is_active=True,
            created_by_id=requester_id
        )

        db.session.add(pricing)
        db.session.commit()

        return UseCaseResult.ok({
            'pricing': pricing.to_dict(include_service=True, include_client=True)
        })
