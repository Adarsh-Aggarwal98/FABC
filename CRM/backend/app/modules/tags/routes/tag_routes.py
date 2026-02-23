"""
Tags Module Routes - Client Tagging API Endpoints

This module provides REST API endpoints for managing tags that can
be assigned to clients for categorization and filtering.

Endpoints:
---------
GET  /api/tags
    List all tags for the company.
    Required role: Accountant or higher

POST /api/tags
    Create a new tag.
    Required role: Admin or higher

PATCH /api/tags/<tag_id>
    Update a tag's name or color.
    Required role: Admin or higher

DELETE /api/tags/<tag_id>
    Delete a tag.
    Required role: Admin or higher

GET  /api/tags/users/<user_id>/tags
    Get all tags assigned to a user.
    Required role: Accountant or higher

POST /api/tags/users/<user_id>/tags
    Assign a tag to a user.
    Required role: Accountant or higher

DELETE /api/tags/users/<user_id>/tags/<tag_id>
    Remove a tag from a user.
    Required role: Accountant or higher

Security Notes:
--------------
- Tags are company-scoped (each company has its own tags)
- Super admin can specify company_id to manage any company's tags
"""
import logging
from flask import request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError as MarshmallowValidationError

from app.common.responses import success_response, error_response
from app.common.decorators import admin_required, accountant_required, get_current_user
from .. import tags_bp
from ..schemas import CreateTagSchema, UpdateTagSchema, AssignTagSchema
from ..usecases import (
    ListTagsUseCase, CreateTagUseCase, UpdateTagUseCase, DeleteTagUseCase,
    AssignTagToUserUseCase, RemoveTagFromUserUseCase, GetUserTagsUseCase
)

# Module-level logger
logger = logging.getLogger(__name__)


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
        'TAG_EXISTS': 409,
        'OPERATION_FAILED': 400
    }
    return status_map.get(error_code, 400)


@tags_bp.route('', methods=['GET'])
@jwt_required()
@accountant_required
def list_tags():
    """
    List all tags for the current user's company.

    Returns array of tags with id, name, color, and usage count.
    """
    user = get_current_user()
    logger.info(f"GET /tags - List tags by user_id={user.id}")

    # Super admin must specify company_id
    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        logger.warning("Tags list requested without company_id")
        return error_response('Company ID required for super admin', 400)

    usecase = ListTagsUseCase()
    result = usecase.execute(company_id)

    if result.success:
        logger.debug(f"Retrieved {len(result.data.get('tags', []))} tags for company_id={company_id}")
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@tags_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_tag():
    """Create a new tag (admin only)"""
    try:
        schema = CreateTagSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    user = get_current_user()
    company_id = request.json.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    usecase = CreateTagUseCase()
    result = usecase.execute(
        company_id=company_id,
        name=data['name'],
        color=data.get('color', '#3B82F6')
    )

    if result.success:
        return success_response(result.data, status_code=201)
    return error_response(result.error, _get_status_code(result.error_code))


@tags_bp.route('/<int:tag_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_tag(tag_id):
    """Update a tag (admin only)"""
    try:
        schema = UpdateTagSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    user = get_current_user()
    company_id = request.json.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    usecase = UpdateTagUseCase()
    result = usecase.execute(tag_id, company_id, data)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_tag(tag_id):
    """Delete a tag (admin only)"""
    user = get_current_user()
    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    usecase = DeleteTagUseCase()
    result = usecase.execute(tag_id, company_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


# User-tag assignment routes

@tags_bp.route('/users/<user_id>/tags', methods=['GET'])
@jwt_required()
@accountant_required
def get_user_tags(user_id):
    """Get all tags for a specific user"""
    usecase = GetUserTagsUseCase()
    result = usecase.execute(user_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@tags_bp.route('/users/<user_id>/tags', methods=['POST'])
@jwt_required()
@accountant_required
def assign_tag_to_user(user_id):
    """Assign a tag to a user"""
    try:
        schema = AssignTagSchema()
        data = schema.load(request.json)
    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)

    user = get_current_user()
    company_id = user.company_id

    # Super admin can specify company
    if user.role.name == 'super_admin':
        company_id = request.json.get('company_id', company_id)

    if not company_id:
        return error_response('Company ID required', 400)

    usecase = AssignTagToUserUseCase()
    result = usecase.execute(user_id, data['tag_id'], company_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@tags_bp.route('/users/<user_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
@accountant_required
def remove_tag_from_user(user_id, tag_id):
    """Remove a tag from a user"""
    user = get_current_user()
    company_id = user.company_id

    # Super admin can specify company
    if user.role.name == 'super_admin':
        company_id = request.args.get('company_id', company_id)

    if not company_id:
        return error_response('Company ID required', 400)

    usecase = RemoveTagFromUserUseCase()
    result = usecase.execute(user_id, tag_id, company_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))
