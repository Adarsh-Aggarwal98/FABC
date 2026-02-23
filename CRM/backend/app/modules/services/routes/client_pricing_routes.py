"""
Client Pricing Routes - API endpoints for client-specific pricing management

Admin-only endpoints for managing client-specific pricing.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError as MarshmallowValidationError

from app.common.decorators import admin_required
from app.common.responses import success_response, error_response
from app.modules.services.usecases.pricing import (
    ListClientPricingUseCase,
    GetClientPricingUseCase,
    CreateClientPricingUseCase,
    UpdateClientPricingUseCase,
    DeleteClientPricingUseCase,
    GetEffectivePriceUseCase,
)


# Create blueprint
client_pricing_bp = Blueprint('client_pricing', __name__, url_prefix='/api/client-pricing')


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
        'NO_COMPANY': 400,
        'INVALID_INPUT': 400,
        'DUPLICATE': 409,
    }
    return status_map.get(error_code, 400)


# ============== Schemas ==============

class CreateClientPricingSchema(Schema):
    service_id = fields.Integer(required=True)
    user_id = fields.String(allow_none=True)
    client_entity_id = fields.String(allow_none=True)
    custom_price = fields.Float(allow_none=True)
    discount_percentage = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    notes = fields.String(allow_none=True)
    valid_from = fields.String(allow_none=True)  # ISO date string
    valid_until = fields.String(allow_none=True)  # ISO date string


class UpdateClientPricingSchema(Schema):
    custom_price = fields.Float(allow_none=True)
    discount_percentage = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    notes = fields.String(allow_none=True)
    valid_from = fields.String(allow_none=True)
    valid_until = fields.String(allow_none=True)
    is_active = fields.Boolean(allow_none=True)


# ============== Routes ==============

@client_pricing_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def list_client_pricing():
    """
    List all client pricing records.

    Query params:
    - user_id: Filter by user
    - client_entity_id: Filter by entity
    - service_id: Filter by service
    - include_inactive: Include inactive records (default: false)
    """
    user_id = get_jwt_identity()

    filter_user_id = request.args.get('user_id')
    filter_entity_id = request.args.get('client_entity_id')
    filter_service_id = request.args.get('service_id', type=int)
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    usecase = ListClientPricingUseCase()
    result = usecase.execute(
        requester_id=user_id,
        user_id=filter_user_id,
        client_entity_id=filter_entity_id,
        service_id=filter_service_id,
        include_inactive=include_inactive
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@client_pricing_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_pricing_for_user(user_id):
    """Get all pricing records for a specific user."""
    requester_id = get_jwt_identity()
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    usecase = ListClientPricingUseCase()
    result = usecase.execute(
        requester_id=requester_id,
        user_id=user_id,
        include_inactive=include_inactive
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@client_pricing_bp.route('/entity/<entity_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_pricing_for_entity(entity_id):
    """Get all pricing records for a specific client entity."""
    requester_id = get_jwt_identity()
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    usecase = ListClientPricingUseCase()
    result = usecase.execute(
        requester_id=requester_id,
        client_entity_id=entity_id,
        include_inactive=include_inactive
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@client_pricing_bp.route('/<pricing_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_client_pricing(pricing_id):
    """Get a specific pricing record by ID."""
    requester_id = get_jwt_identity()

    usecase = GetClientPricingUseCase()
    result = usecase.execute(pricing_id, requester_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@client_pricing_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_client_pricing():
    """Create a new client pricing record."""
    try:
        schema = CreateClientPricingSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    requester_id = get_jwt_identity()

    usecase = CreateClientPricingUseCase()
    result = usecase.execute(
        requester_id=requester_id,
        service_id=data['service_id'],
        user_id=data.get('user_id'),
        client_entity_id=data.get('client_entity_id'),
        custom_price=data.get('custom_price'),
        discount_percentage=data.get('discount_percentage'),
        notes=data.get('notes'),
        valid_from=data.get('valid_from'),
        valid_until=data.get('valid_until')
    )

    if result.success:
        return success_response(result.data, message='Client pricing created successfully', status_code=201)
    return error_response(result.error, _get_status_code(result.error_code))


@client_pricing_bp.route('/<pricing_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_client_pricing(pricing_id):
    """Update a client pricing record."""
    try:
        schema = UpdateClientPricingSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    requester_id = get_jwt_identity()

    usecase = UpdateClientPricingUseCase()
    result = usecase.execute(
        pricing_id=pricing_id,
        requester_id=requester_id,
        **data
    )

    if result.success:
        return success_response(result.data, message='Client pricing updated successfully')
    return error_response(result.error, _get_status_code(result.error_code))


@client_pricing_bp.route('/<pricing_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_client_pricing(pricing_id):
    """Delete (deactivate) a client pricing record."""
    requester_id = get_jwt_identity()

    usecase = DeleteClientPricingUseCase()
    result = usecase.execute(pricing_id, requester_id)

    if result.success:
        return success_response(result.data, message='Client pricing deleted successfully')
    return error_response(result.error, _get_status_code(result.error_code))


# ============== Effective Price Endpoint ==============

@client_pricing_bp.route('/effective-price/<int:service_id>', methods=['GET'])
@jwt_required()
def get_effective_price(service_id):
    """
    Get the effective price for a service.

    Query params:
    - user_id: User to get price for
    - client_entity_id: Entity to get price for

    Note: Only staff can access this endpoint.
    """
    requester_id = get_jwt_identity()

    user_id = request.args.get('user_id')
    client_entity_id = request.args.get('client_entity_id')

    usecase = GetEffectivePriceUseCase()
    result = usecase.execute(
        service_id=service_id,
        requester_id=requester_id,
        user_id=user_id,
        client_entity_id=client_entity_id
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))
