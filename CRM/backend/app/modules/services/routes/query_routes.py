"""
Query Routes - Thin Controllers for message/query operations

These routes handle HTTP concerns and delegate business logic to use cases.
"""
from flask import request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError as MarshmallowValidationError

from . import requests_bp
from app.modules.services.usecases import CreateQueryUseCase, GetQueriesUseCase
from app.modules.services.schemas import CreateQuerySchema
from app.modules.services.models import ServiceRequest, Query
from app.common.decorators import get_current_user
from app.common.responses import success_response, error_response
from app.extensions import db


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
    }
    return status_map.get(error_code, 400)


@requests_bp.route('/<request_id>/queries', methods=['GET'])
@jwt_required()
def get_queries(request_id):
    """Get all queries for a request (internal notes filtered by role)"""
    current_user = get_current_user()
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return error_response('Request not found', 404)

    # Check access
    is_staff = current_user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
    is_owner = service_request.user_id == current_user.id

    if not is_staff and not is_owner:
        return error_response('Access denied', 403)

    # Build query - staff can see all, clients only see non-internal
    query = Query.query.filter_by(service_request_id=request_id)
    if not is_staff:
        query = query.filter_by(is_internal=False)

    queries = query.order_by(Query.created_at.asc()).all()

    return success_response({
        'queries': [q.to_dict() for q in queries],
        'total': len(queries)
    })


@requests_bp.route('/<request_id>/queries', methods=['POST'])
@jwt_required()
def create_query(request_id):
    """Create a query on a request (supports internal messages for staff)"""
    current_user = get_current_user()
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return error_response('Request not found', 404)

    # Check access
    is_staff = current_user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
    is_owner = service_request.user_id == current_user.id

    if not is_staff and not is_owner:
        return error_response('Access denied', 403)

    message = request.json.get('message')
    if not message:
        return error_response('Message is required', 400)

    attachment_url = request.json.get('attachment_url')
    is_internal = request.json.get('is_internal', False)

    # Only staff can create internal messages
    if is_internal and not is_staff:
        is_internal = False

    usecase = CreateQueryUseCase()
    result = usecase.execute(
        request_id=request_id,
        sender_id=current_user.id,
        message=message,
        attachment_url=attachment_url,
        is_internal=is_internal
    )

    if result.success:
        return success_response(
            {'query': result.data['query']},
            message='Message posted successfully',
            status_code=201
        )
    return error_response(result.error, _get_status_code(result.error_code))
