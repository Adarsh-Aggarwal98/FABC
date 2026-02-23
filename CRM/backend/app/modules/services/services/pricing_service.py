"""
PricingService - Service for resolving client-specific pricing
"""
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import date

from app.extensions import db
from app.modules.services.models import Service, ClientServicePricing


class PricingService:
    """
    Service for resolving effective prices for clients.

    Price Resolution Order:
    1. Check client_entity pricing (if client_entity_id provided)
    2. Check user pricing (if user_id provided)
    3. Fall back to Service.base_price
    """

    @staticmethod
    def get_effective_price(
        service_id: int,
        user_id: Optional[str] = None,
        client_entity_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the effective price for a service for a specific client.

        Args:
            service_id: The service ID
            user_id: Optional user (client) ID
            client_entity_id: Optional client entity ID
            company_id: Optional company ID for filtering

        Returns:
            Dictionary with price info:
            {
                'price': Decimal or None,
                'source': 'entity_pricing' | 'user_pricing' | 'base_price' | 'no_price',
                'pricing_record_id': str or None,
                'discount_percentage': float or None,
                'notes': str or None
            }
        """
        service = Service.query.get(service_id)
        if not service:
            return {
                'price': None,
                'source': 'no_price',
                'pricing_record_id': None,
                'discount_percentage': None,
                'notes': None
            }

        base_price = service.base_price

        # 1. Check client_entity pricing first (takes precedence)
        if client_entity_id:
            entity_pricing = PricingService._get_valid_pricing(
                service_id=service_id,
                client_entity_id=client_entity_id,
                company_id=company_id
            )
            if entity_pricing:
                return PricingService._build_price_response(
                    entity_pricing, base_price, 'entity_pricing'
                )

        # 2. Check user pricing
        if user_id:
            user_pricing = PricingService._get_valid_pricing(
                service_id=service_id,
                user_id=user_id,
                company_id=company_id
            )
            if user_pricing:
                return PricingService._build_price_response(
                    user_pricing, base_price, 'user_pricing'
                )

        # 3. Fall back to base price
        return {
            'price': float(base_price) if base_price else None,
            'source': 'base_price',
            'pricing_record_id': None,
            'discount_percentage': None,
            'notes': None
        }

    @staticmethod
    def _get_valid_pricing(
        service_id: int,
        user_id: Optional[str] = None,
        client_entity_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Optional[ClientServicePricing]:
        """Get a valid (active and within date range) pricing record."""
        query = ClientServicePricing.query.filter_by(
            service_id=service_id,
            is_active=True
        )

        if user_id:
            query = query.filter_by(user_id=user_id)
        elif client_entity_id:
            query = query.filter_by(client_entity_id=client_entity_id)
        else:
            return None

        if company_id:
            query = query.filter_by(company_id=company_id)

        pricing = query.first()

        if pricing and pricing.is_valid_now():
            return pricing

        return None

    @staticmethod
    def _build_price_response(
        pricing: ClientServicePricing,
        base_price: Optional[Decimal],
        source: str
    ) -> Dict[str, Any]:
        """Build the price response dictionary from a pricing record."""
        calculated_price = pricing.calculate_price(base_price) if base_price else pricing.custom_price

        return {
            'price': float(calculated_price) if calculated_price else None,
            'source': source,
            'pricing_record_id': pricing.id,
            'discount_percentage': float(pricing.discount_percentage) if pricing.discount_percentage else None,
            'notes': pricing.notes
        }

    @staticmethod
    def get_all_pricing_for_service(
        service_id: int,
        company_id: str,
        include_inactive: bool = False
    ) -> list:
        """
        Get all client pricing records for a service.

        Args:
            service_id: The service ID
            company_id: The company ID
            include_inactive: Whether to include inactive pricing records

        Returns:
            List of ClientServicePricing records
        """
        query = ClientServicePricing.query.filter_by(
            service_id=service_id,
            company_id=company_id
        )

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.all()

    @staticmethod
    def get_pricing_for_user(
        user_id: str,
        company_id: str,
        include_inactive: bool = False
    ) -> list:
        """Get all pricing records for a specific user."""
        query = ClientServicePricing.query.filter_by(
            user_id=user_id,
            company_id=company_id
        )

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.all()

    @staticmethod
    def get_pricing_for_entity(
        client_entity_id: str,
        company_id: str,
        include_inactive: bool = False
    ) -> list:
        """Get all pricing records for a specific client entity."""
        query = ClientServicePricing.query.filter_by(
            client_entity_id=client_entity_id,
            company_id=company_id
        )

        if not include_inactive:
            query = query.filter_by(is_active=True)

        return query.all()

    @staticmethod
    def get_suggested_price_for_invoice(
        service_id: int,
        user_id: str,
        client_entity_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the suggested price for an invoice.
        This is a convenience method that returns price info
        formatted for use in invoice creation.

        Returns:
            Dictionary with:
            {
                'suggested_price': float or None,
                'price_source': str,
                'has_custom_pricing': bool,
                'pricing_notes': str or None
            }
        """
        price_info = PricingService.get_effective_price(
            service_id=service_id,
            user_id=user_id,
            client_entity_id=client_entity_id,
            company_id=company_id
        )

        return {
            'suggested_price': price_info['price'],
            'price_source': price_info['source'],
            'has_custom_pricing': price_info['source'] in ('entity_pricing', 'user_pricing'),
            'pricing_notes': price_info['notes']
        }
