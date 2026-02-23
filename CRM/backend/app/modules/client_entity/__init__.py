"""
ClientEntity Module
====================
Handles client organizations (companies, trusts, SMSFs, etc.) and their contacts.
Enables external accountants to manage multiple clients and preserves history across POC changes.

Clean Architecture Structure:
-----------------------------
client_entity/
    models/          - Domain models (ClientEntity, ClientEntityContact)
    repositories/    - Data access layer
    usecases/        - Business logic / use cases
    schemas/         - Validation and serialization schemas
    routes/          - HTTP route handlers (thin controllers)
"""

from flask import Blueprint

# Create blueprint
client_entity_bp = Blueprint('client_entity', __name__, url_prefix='/client-entities')

# Import routes to register them (new structure)
from .routes import client_entity_routes, contact_routes, service_request_routes  # noqa: F401, E402
