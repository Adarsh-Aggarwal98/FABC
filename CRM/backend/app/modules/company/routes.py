"""
Company Routes (Backward Compatibility)
=======================================

This module imports routes from the routes/ package to register them on company_bp.
The actual route definitions are in routes/company_routes.py.

New code should refer to routes/company_routes.py for route implementations.
"""
# Import routes from the routes package (this registers them on company_bp)
from app.modules.company.routes import company_routes

# Note: Routes are automatically registered when imported as they use @company_bp decorators
