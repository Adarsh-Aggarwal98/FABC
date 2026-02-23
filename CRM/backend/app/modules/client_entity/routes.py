"""
ClientEntity Routes - Backward Compatibility
=============================================
This file exists for backward compatibility.

Routes are now organized in the routes/ subdirectory:
    - routes/client_entity_routes.py - Entity CRUD endpoints
    - routes/contact_routes.py - Contact management endpoints
    - routes/service_request_routes.py - Service request endpoints

All routes are automatically registered via the routes/__init__.py
which is imported in the main __init__.py.

Entity Endpoints (/api/client-entities):
---------------------------------------
GET  /api/client-entities/my-entities
GET  /api/client-entities
GET  /api/client-entities/search
POST /api/client-entities
GET  /api/client-entities/<entity_id>
PATCH /api/client-entities/<entity_id>
DELETE /api/client-entities/<entity_id>

Contact Endpoints:
-----------------
GET  /api/client-entities/<entity_id>/contacts
POST /api/client-entities/<entity_id>/contacts
PATCH /api/client-entities/<entity_id>/contacts/<contact_id>
POST /api/client-entities/<entity_id>/contacts/<contact_id>/end

Service Requests:
----------------
GET  /api/client-entities/<entity_id>/service-requests
"""

# Routes are now registered via routes/__init__.py
# This file is kept for documentation and backward compatibility
