"""
Status Routes
==============
API endpoints for request status management.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.modules.services.schemas.status_schemas import (
    CreateStatusSchema,
    UpdateStatusSchema,
    ReorderStatusesSchema,
    InitializeCustomStatusesSchema
)
from app.modules.services.usecases.status import (
    GetStatusesUseCase,
    GetSystemStatusesUseCase,
    InitializeCustomStatusesUseCase,
    CreateCustomStatusUseCase,
    UpdateCustomStatusUseCase,
    DeleteCustomStatusUseCase,
    ReorderStatusesUseCase,
    ResetToSystemDefaultsUseCase,
    GetStatusForRequestUseCase
)
from app.modules.services.models.status_transition import StatusTransition
from app.modules.services.services.status_resolver import TransitionResolver
from app.modules.user.models import User, Role
from app.extensions import db

# Create blueprint
status_bp = Blueprint('statuses', __name__, url_prefix='/api/statuses')


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


# ============================================================================
# STATUS ENDPOINTS
# ============================================================================

@status_bp.route('', methods=['GET'])
@jwt_required()
def get_statuses():
    """
    Get statuses for the current user's company.
    Returns custom statuses if company has customized, otherwise system defaults.

    Query params:
        - include_inactive: Include inactive statuses (default: false)
        - category: Filter by category (request, task, both)
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    category = request.args.get('category')

    # Execute use case
    use_case = GetStatusesUseCase()
    result = use_case.execute(company_id=company_id, include_inactive=include_inactive, category=category)

    if not result.success:
        return error_response(result.error, 500)

    return success_response(result.data)


@status_bp.route('/system', methods=['GET'])
@jwt_required()
def get_system_statuses():
    """
    Get system default statuses.
    Useful for admins to see what defaults are available.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    # Execute use case
    use_case = GetSystemStatusesUseCase()
    result = use_case.execute()

    if not result.success:
        return error_response(result.error, 500)

    return success_response(result.data)


@status_bp.route('/initialize', methods=['POST'])
@jwt_required()
def initialize_custom_statuses():
    """
    Initialize custom statuses by copying system defaults.
    This enables the company to customize their status columns.

    Admin only.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can initialize custom statuses', 403)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Execute use case
    use_case = InitializeCustomStatusesUseCase()
    result = use_case.execute(company_id=company_id)

    if not result.success:
        status_code = 409 if result.error_code == 'ALREADY_CUSTOMIZED' else 500
        return error_response(result.error, status_code)

    return success_response(result.data, 201)


@status_bp.route('', methods=['POST'])
@jwt_required()
def create_status():
    """
    Create a new custom status.

    Admin only.

    Body:
        - status_key: Unique key for the status (lowercase, underscores)
        - display_name: Display name for the status
        - description: Optional description
        - color: Hex color code (e.g., #3B82F6)
        - position: Position in column order (optional, defaults to end)
        - wip_limit: Work-in-progress limit (optional)
        - is_final: Whether this is a final state (completed/cancelled)
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can create statuses', 403)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = CreateStatusSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = CreateCustomStatusUseCase()
    result = use_case.execute(company_id=company_id, **data)

    if not result.success:
        status_code = 409 if result.error_code == 'DUPLICATE_KEY' else 500
        return error_response(result.error, status_code)

    return success_response(result.data, 201)


@status_bp.route('/<int:status_id>', methods=['PATCH'])
@jwt_required()
def update_status(status_id):
    """
    Update a custom status.

    Admin only.

    Body (all optional):
        - display_name: Display name for the status
        - description: Description
        - color: Hex color code
        - position: Position in column order
        - wip_limit: Work-in-progress limit (null to remove)
        - is_final: Whether this is a final state
        - is_active: Whether status is active
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can update statuses', 403)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = UpdateStatusSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = UpdateCustomStatusUseCase()
    result = use_case.execute(
        status_id=status_id,
        company_id=company_id,
        updates=data
    )

    if not result.success:
        status_code = 404 if result.error_code == 'NOT_FOUND' else 500
        return error_response(result.error, status_code)

    return success_response(result.data)


@status_bp.route('/<int:status_id>', methods=['DELETE'])
@jwt_required()
def delete_status(status_id):
    """
    Delete a custom status (soft delete).

    Admin only.

    Note: Cannot delete if any requests are using this status.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can delete statuses', 403)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Execute use case
    use_case = DeleteCustomStatusUseCase()
    result = use_case.execute(status_id=status_id, company_id=company_id)

    if not result.success:
        if result.error_code == 'NOT_FOUND':
            return error_response(result.error, 404)
        elif result.error_code == 'STATUS_IN_USE':
            return error_response(result.error, 409)
        return error_response(result.error, 500)

    return success_response(result.data)


@status_bp.route('/reorder', methods=['POST'])
@jwt_required()
def reorder_statuses():
    """
    Reorder custom statuses.

    Admin only.

    Body:
        - status_ids: Ordered list of status IDs
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can reorder statuses', 403)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Validate input
    try:
        schema = ReorderStatusesSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response(str(e.messages), 400)

    # Execute use case
    use_case = ReorderStatusesUseCase()
    result = use_case.execute(
        company_id=company_id,
        status_ids=data['status_ids']
    )

    if not result.success:
        status_code = 400 if result.error_code == 'INVALID_STATUS_ID' else 500
        return error_response(result.error, status_code)

    return success_response(result.data)


@status_bp.route('/reset', methods=['POST'])
@jwt_required()
def reset_to_defaults():
    """
    Reset company statuses to system defaults.

    Admin only.

    This deletes all custom statuses, reverting to system defaults.
    Cannot reset if requests are using statuses that don't exist in system defaults.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can reset statuses', 403)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Execute use case
    use_case = ResetToSystemDefaultsUseCase()
    result = use_case.execute(company_id=company_id)

    if not result.success:
        status_code = 409 if result.error_code == 'CUSTOM_STATUS_IN_USE' else 500
        return error_response(result.error, status_code)

    return success_response(result.data)


@status_bp.route('/lookup/<status_key>', methods=['GET'])
@jwt_required()
def lookup_status(status_key):
    """
    Look up a status by its key.

    Returns the status configuration (color, display name, etc.) for a given status key.
    Checks company custom statuses first, then falls back to system defaults.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    company_id = current_user.company_id
    if not company_id:
        return error_response('Company not found', 400)

    # Execute use case
    use_case = GetStatusForRequestUseCase()
    result = use_case.execute(company_id=company_id, status_key=status_key)

    if not result.success:
        status_code = 404 if result.error_code == 'NOT_FOUND' else 500
        return error_response(result.error, status_code)

    return success_response(result.data)


# ============================================================================
# TRANSITION ENDPOINTS
# ============================================================================

@status_bp.route('/transitions', methods=['GET'])
@jwt_required()
def get_transitions():
    """
    Get transition rules for the current company.
    Falls back to system defaults if no company-specific rules.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    company_id = current_user.company_id

    # Get company transitions first, fallback to system
    transitions = StatusTransition.query.filter_by(company_id=company_id).all()
    if not transitions:
        transitions = StatusTransition.query.filter_by(company_id=None).all()

    return success_response({
        'transitions': [t.to_dict() for t in transitions]
    })


@status_bp.route('/transitions/allowed', methods=['GET'])
@jwt_required()
def get_allowed_transitions():
    """
    Get allowed target statuses for a given from_status and current user.

    Query params:
        - from_status: Current status key (required)
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    from_status = request.args.get('from_status')
    if not from_status:
        return error_response('from_status is required', 400)

    company_id = current_user.company_id
    user_role = current_user.role.name if current_user.role else None

    allowed = TransitionResolver.get_allowed_transitions(
        company_id, from_status, user_role
    )

    return success_response({
        'from_status': from_status,
        'allowed_targets': allowed
    })


@status_bp.route('/transitions', methods=['POST'])
@jwt_required()
def create_transition():
    """
    Create a transition rule. Admin only.

    Body:
        - from_status_key: Source status key
        - to_status_key: Target status key
        - allowed_roles: List of role names (optional, null = all)
        - requires_note: Whether a note is required (default: false)
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can manage transitions', 403)

    data = request.json or {}
    if not data.get('from_status_key') or not data.get('to_status_key'):
        return error_response('from_status_key and to_status_key are required', 400)

    company_id = current_user.company_id

    transition = StatusTransition(
        from_status_key=data['from_status_key'],
        to_status_key=data['to_status_key'],
        allowed_roles=data.get('allowed_roles'),
        requires_note=data.get('requires_note', False),
        company_id=company_id
    )

    try:
        db.session.add(transition)
        db.session.commit()
        return success_response({'transition': transition.to_dict()}, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 409)


@status_bp.route('/transitions/<int:transition_id>', methods=['PATCH'])
@jwt_required()
def update_transition(transition_id):
    """Update a transition rule. Admin only."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can manage transitions', 403)

    transition = StatusTransition.query.filter_by(
        id=transition_id,
        company_id=current_user.company_id
    ).first()
    if not transition:
        return error_response('Transition not found', 404)

    data = request.json or {}
    if 'allowed_roles' in data:
        transition.allowed_roles = data['allowed_roles']
    if 'requires_note' in data:
        transition.requires_note = data['requires_note']

    db.session.commit()
    return success_response({'transition': transition.to_dict()})


@status_bp.route('/transitions/<int:transition_id>', methods=['DELETE'])
@jwt_required()
def delete_transition(transition_id):
    """Delete a transition rule. Admin only."""
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return error_response('Only admins can manage transitions', 403)

    transition = StatusTransition.query.filter_by(
        id=transition_id,
        company_id=current_user.company_id
    ).first()
    if not transition:
        return error_response('Transition not found', 404)

    db.session.delete(transition)
    db.session.commit()
    return success_response({'message': 'Transition deleted'})
