"""
ClientEntity Routes
====================
REST API endpoints for managing client entities.

Entity Endpoints (/api/client-entities):
---------------------------------------
GET  /api/client-entities/my-entities
    Get entities where the current user is a contact.
    Required role: Any authenticated user

GET  /api/client-entities
    List client entities for the company.
    Query params: entity_type, is_active, page, per_page, sort_by, sort_order
    Required role: Accountant or higher

GET  /api/client-entities/search
    Search entities by name or ABN.
    Query params: q (required), entity_type, is_active
    Required role: Accountant or higher

POST /api/client-entities
    Create a new client entity.
    Required role: Admin or higher

GET  /api/client-entities/<entity_id>
    Get entity details.
    Required role: Accountant or higher

PATCH /api/client-entities/<entity_id>
    Update an entity.
    Required role: Admin or higher

DELETE /api/client-entities/<entity_id>
    Soft delete an entity.
    Required role: Admin or higher
"""

import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .. import client_entity_bp
from ..models import ClientEntity, ClientEntityContact
from ..schemas import (
    CreateClientEntitySchema,
    UpdateClientEntitySchema,
    ClientEntityListSchema,
    ClientEntitySearchSchema,
)
from ..usecases import (
    CreateClientEntityUseCase,
    UpdateClientEntityUseCase,
    DeleteClientEntityUseCase,
    ListClientEntitiesUseCase,
    SearchClientEntitiesUseCase,
)
from ..repositories import ClientEntityRepository
from app.modules.user.models import User, Role

# Module-level logger
logger = logging.getLogger(__name__)


def get_current_user():
    """Get the current authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def error_response(message: str, status_code: int = 400):
    """Create an error response."""
    return jsonify({'error': message}), status_code


def success_response(data: dict, status_code: int = 200):
    """Create a success response."""
    return jsonify(data), status_code


@client_entity_bp.route('/my-entities', methods=['GET'])
@jwt_required()
def get_my_entities():
    """
    Get entities where the current user is a contact.
    This allows regular users to see their linked entities.
    """
    current_user = get_current_user()
    logger.info(f"GET /client-entities/my-entities - Request by user_id={current_user.id if current_user else 'unknown'}")
    if not current_user:
        return error_response('User not found', 404)

    # Find all contacts where this user is linked
    contacts = ClientEntityContact.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).filter(
        ClientEntityContact.effective_to.is_(None)
    ).all()

    # Get unique entity IDs
    entity_ids = list(set([c.client_entity_id for c in contacts]))

    if not entity_ids:
        return success_response({
            'entities': [],
            'total': 0
        })

    # Get the entities
    entities = ClientEntity.query.filter(
        ClientEntity.id.in_(entity_ids),
        ClientEntity.is_active == True
    ).order_by(ClientEntity.name).all()

    return success_response({
        'entities': [e.to_dict(include_primary_contact=True) for e in entities],
        'total': len(entities)
    })


@client_entity_bp.route('', methods=['GET'])
@jwt_required()
def list_entities():
    """
    List client entities for the current user's company.

    Query params:
        - entity_type: Filter by type (COMPANY, TRUST, etc.)
        - is_active: Filter by active status
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - sort_by: Sort field (name, created_at, updated_at, entity_type)
        - sort_order: Sort order (asc, desc)
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    # Only admins, accountants can list entities
    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT, Role.SENIOR_ACCOUNTANT, Role.EXTERNAL_ACCOUNTANT]:
        return error_response('Access denied', 403)

    # Get company_id
    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        # Super admin can specify company
        company_id = request.args.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Validate params
    try:
        schema = ClientEntityListSchema()
        params = schema.load(request.args)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = ListClientEntitiesUseCase()
    result = use_case.execute(
        company_id=company_id,
        entity_type=params.get('entity_type'),
        is_active=params.get('is_active'),
        page=params.get('page', 1),
        per_page=params.get('per_page', 20),
        sort_by=params.get('sort_by', 'name'),
        sort_order=params.get('sort_order', 'asc')
    )

    if not result.success:
        return error_response(result.error, 500)

    return success_response(result.data)


@client_entity_bp.route('/search', methods=['GET'])
@jwt_required()
def search_entities():
    """
    Search client entities by name or ABN.

    Query params:
        - q: Search query (required)
        - entity_type: Filter by type
        - is_active: Filter by active status
        - page: Page number
        - per_page: Items per page
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT, Role.SENIOR_ACCOUNTANT, Role.EXTERNAL_ACCOUNTANT]:
        return error_response('Access denied', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.args.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Validate params
    try:
        schema = ClientEntitySearchSchema()
        params = schema.load(request.args)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    if not params.get('q'):
        return error_response('Search query is required', 400)

    # Execute use case
    use_case = SearchClientEntitiesUseCase()
    result = use_case.execute(
        company_id=company_id,
        query=params['q'],
        entity_type=params.get('entity_type'),
        is_active=params.get('is_active'),
        page=params.get('page', 1),
        per_page=params.get('per_page', 20)
    )

    if not result.success:
        return error_response(result.error, 500)

    return success_response(result.data)


@client_entity_bp.route('', methods=['POST'])
@jwt_required()
def create_entity():
    """
    Create a new client entity.

    Body:
        - name: Entity name (required)
        - entity_type: Type (required, e.g., COMPANY, TRUST)
        - trading_name, abn, acn, tfn: Optional identifiers
        - trust_type, trustee_name, trust_deed_date: Trust-specific
        - email, phone: Contact info
        - address_*: Address fields
        - primary_contact: Optional initial contact
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can create client entities', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.json.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = CreateClientEntitySchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = CreateClientEntityUseCase()
    result = use_case.execute(
        company_id=company_id,
        created_by_id=current_user.id,
        **data
    )

    if not result.success:
        status_code = 409 if result.error_code == 'DUPLICATE_NAME' else 500
        return error_response(result.error, status_code)

    return success_response(result.data, 201)


@client_entity_bp.route('/<entity_id>', methods=['GET'])
@jwt_required()
def get_entity(entity_id):
    """Get a client entity by ID."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT, Role.SENIOR_ACCOUNTANT, Role.EXTERNAL_ACCOUNTANT]:
        return error_response('Access denied', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.args.get('company_id', company_id)

    # Get entity
    repo = ClientEntityRepository()
    entity = repo.get_by_id_and_company(entity_id, company_id) if company_id else repo.get_by_id(entity_id)

    if not entity:
        return error_response('Entity not found', 404)

    include_contacts = request.args.get('include_contacts', 'false').lower() == 'true'

    return success_response({
        'entity': entity.to_dict(include_contacts=include_contacts, include_primary_contact=True)
    })


@client_entity_bp.route('/<entity_id>', methods=['PATCH'])
@jwt_required()
def update_entity(entity_id):
    """Update a client entity."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can update client entities', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.json.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = UpdateClientEntitySchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = UpdateClientEntityUseCase()
    result = use_case.execute(
        entity_id=entity_id,
        company_id=company_id,
        updates=data
    )

    if not result.success:
        status_code = 404 if result.error_code == 'NOT_FOUND' else 500
        return error_response(result.error, status_code)

    return success_response(result.data)


@client_entity_bp.route('/<entity_id>', methods=['DELETE'])
@jwt_required()
def delete_entity(entity_id):
    """Soft delete a client entity."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can delete client entities', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.args.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Execute use case
    use_case = DeleteClientEntityUseCase()
    result = use_case.execute(entity_id=entity_id, company_id=company_id)

    if not result.success:
        status_code = 404 if result.error_code == 'NOT_FOUND' else 500
        return error_response(result.error, status_code)

    return success_response(result.data)
