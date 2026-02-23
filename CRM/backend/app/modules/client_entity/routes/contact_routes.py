"""
ClientEntity Contact Routes
============================
REST API endpoints for managing client entity contacts.

Contact Endpoints:
-----------------
GET  /api/client-entities/<entity_id>/contacts
    List contacts for an entity.
    Required role: Accountant or higher

POST /api/client-entities/<entity_id>/contacts
    Add a contact to an entity.
    Required role: Admin or higher

PATCH /api/client-entities/<entity_id>/contacts/<contact_id>
    Update a contact.
    Required role: Admin or higher

POST /api/client-entities/<entity_id>/contacts/<contact_id>/end
    End a contact's effective period.
    Required role: Admin or higher
"""

import logging
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from .. import client_entity_bp
from ..schemas import (
    CreateClientEntityContactSchema,
    UpdateClientEntityContactSchema,
)
from ..usecases import (
    AddContactUseCase,
    UpdateContactUseCase,
    EndContactUseCase,
)
from ..repositories import ClientEntityRepository, ClientEntityContactRepository
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


@client_entity_bp.route('/<entity_id>/contacts', methods=['GET'])
@jwt_required()
def list_contacts(entity_id):
    """List contacts for a client entity."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
        return error_response('Access denied', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.args.get('company_id', company_id)

    # Verify entity exists
    entity_repo = ClientEntityRepository()
    entity = entity_repo.get_by_id_and_company(entity_id, company_id) if company_id else entity_repo.get_by_id(entity_id)
    if not entity:
        return error_response('Entity not found', 404)

    # Get contacts
    include_history = request.args.get('include_history', 'false').lower() == 'true'
    contact_repo = ClientEntityContactRepository()

    if include_history:
        contacts = contact_repo.list_by_entity_with_history(entity_id)
    else:
        contacts = contact_repo.list_by_entity(entity_id)

    return success_response({
        'contacts': [c.to_dict() for c in contacts]
    })


@client_entity_bp.route('/<entity_id>/contacts', methods=['POST'])
@jwt_required()
def add_contact(entity_id):
    """Add a contact to a client entity."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can add contacts', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.json.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = CreateClientEntityContactSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = AddContactUseCase()
    result = use_case.execute(
        entity_id=entity_id,
        company_id=company_id,
        **data
    )

    if not result.success:
        status_code = 404 if result.error_code == 'NOT_FOUND' else 500
        return error_response(result.error, status_code)

    return success_response(result.data, 201)


@client_entity_bp.route('/<entity_id>/contacts/<int:contact_id>', methods=['PATCH'])
@jwt_required()
def update_contact(entity_id, contact_id):
    """Update a contact."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can update contacts', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.json.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = UpdateClientEntityContactSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = UpdateContactUseCase()
    result = use_case.execute(
        entity_id=entity_id,
        contact_id=contact_id,
        company_id=company_id,
        updates=data
    )

    if not result.success:
        status_code = 404 if 'NOT_FOUND' in result.error_code else 500
        return error_response(result.error, status_code)

    return success_response(result.data)


@client_entity_bp.route('/<entity_id>/contacts/<int:contact_id>/end', methods=['POST'])
@jwt_required()
def end_contact(entity_id, contact_id):
    """End a contact's effective period."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can end contacts', 403)

    company_id = current_user.company_id
    if current_user.role.name == Role.SUPER_ADMIN:
        company_id = request.json.get('company_id', company_id)

    if not company_id:
        return error_response('Company not found', 400)

    # Get optional params
    end_date = None
    if request.json.get('end_date'):
        end_date = datetime.strptime(request.json['end_date'], '%Y-%m-%d').date()
    reason = request.json.get('reason')

    # Execute use case
    use_case = EndContactUseCase()
    result = use_case.execute(
        entity_id=entity_id,
        contact_id=contact_id,
        company_id=company_id,
        end_date=end_date,
        reason=reason
    )

    if not result.success:
        status_code = 404 if 'NOT_FOUND' in result.error_code else 500
        return error_response(result.error, status_code)

    return success_response(result.data)
