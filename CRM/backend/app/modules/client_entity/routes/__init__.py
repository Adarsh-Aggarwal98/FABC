"""
ClientEntity Routes
====================
Re-export route modules for registration.

All routes are registered on the client_entity_bp blueprint
which is defined in the parent __init__.py.
"""

# Import route modules to register them on the blueprint
from . import client_entity_routes  # noqa: F401
from . import contact_routes  # noqa: F401
from . import service_request_routes  # noqa: F401
