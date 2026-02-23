"""
Payments Module - Stripe payment gateway integration

This module follows clean architecture pattern with:
- services/ - Business logic layer (StripeService)
- routes/ - API route handlers (payment_routes)

Backward Compatibility:
- StripeService is exported at module level for existing imports
- payments_bp Blueprint is exported for Flask app registration
"""
from flask import Blueprint

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

# Import routes to register them with the blueprint
from app.modules.payments.routes import payment_routes  # noqa

# Backward compatibility exports
from app.modules.payments.services.stripe_service import StripeService  # noqa

__all__ = ['payments_bp', 'StripeService']
