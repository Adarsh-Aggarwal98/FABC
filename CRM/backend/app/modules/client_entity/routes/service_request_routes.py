"""
ClientEntity Service Request Routes
=====================================
REST API endpoints for service requests associated with client entities.

Service Requests:
----------------
GET  /api/client-entities/<entity_id>/service-requests
    List service requests for an entity.
    Required role: Accountant or higher
"""

import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import client_entity_bp
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


@client_entity_bp.route('/<entity_id>/service-requests', methods=['GET'])
@jwt_required()
def list_entity_requests(entity_id):
    """List service requests for a client entity."""
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

    # Import ServiceRequest here to avoid circular imports
    from app.modules.services.models import ServiceRequest

    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Query requests
    query = ServiceRequest.query.filter_by(client_entity_id=entity_id)

    # Apply status filter if provided
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    # Order by created_at desc
    query = query.order_by(ServiceRequest.created_at.desc())

    # Paginate
    total = query.count()
    requests = query.offset((page - 1) * per_page).limit(per_page).all()

    return success_response({
        'requests': [r.to_dict() for r in requests],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })
