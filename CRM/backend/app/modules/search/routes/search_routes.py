"""
Search Routes - Thin controller layer for search API endpoints

This module provides REST API endpoints for searching across multiple
entity types (users, service requests, documents) with advanced filtering.
Routes delegate to use cases for business logic.
"""
import logging

from flask import request, Blueprint
from flask_jwt_extended import jwt_required

from app.common.responses import success_response, error_response
from app.common.decorators import accountant_required, get_current_user
from ..usecases.search_usecase import get_search_usecase

# Module-level logger
logger = logging.getLogger(__name__)

# Create blueprint for routes
search_routes_bp = Blueprint('search_routes', __name__)


@search_routes_bp.route('', methods=['GET'])
@jwt_required()
@accountant_required
def global_search():
    """
    Global search across all entities.

    Searches users, service requests, and documents simultaneously.
    Results are grouped by entity type for easy consumption.

    Query parameters:
    - q: Search query string (required, min 1 char)
    - type: Filter to single entity type ('all', 'users', 'requests', 'documents')
    - limit: Max results per entity type (default: 10)
    - company_id: Company filter (super_admin only)

    Returns:
    - users: Matching users with basic info
    - requests: Matching service requests with status
    - documents: Matching documents with metadata
    """
    user = get_current_user()
    logger.info(f"GET /search - Global search by user_id={user.id}")

    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    limit = request.args.get('limit', 10, type=int)

    # Get company_id - super_admin can search any company
    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id
    logger.debug(f"Search params: query='{query}', type={search_type}, limit={limit}, company_id={company_id}")

    if not query:
        logger.warning("Search attempted without query string")
        return error_response('Search query is required', 400)

    # Get use case and execute search
    use_case = get_search_usecase()

    if search_type == 'all':
        logger.debug("Performing global search across all entity types")
        results = use_case.search_all(query, company_id, limit_per_type=limit)
    elif search_type == 'users':
        results = {'users': use_case.search_users(query, company_id, limit=limit)}
    elif search_type == 'requests':
        results = {'requests': use_case.search_requests(query, company_id, limit=limit)}
    elif search_type == 'documents':
        results = {'documents': use_case.search_documents(query, company_id, limit=limit)}
    else:
        logger.warning(f"Invalid search type requested: {search_type}")
        return error_response('Invalid search type', 400)

    # Log result counts
    result_counts = {k: len(v) if isinstance(v, list) else 0 for k, v in results.items()}
    logger.info(f"Search completed for query='{query}': {result_counts}")

    return success_response(results)


@search_routes_bp.route('/users', methods=['GET'])
@jwt_required()
@accountant_required
def search_users():
    """
    Search users with advanced filters.

    Performs full-text search on user names and emails with optional
    filtering by role and tags.

    Query parameters:
    - q: Search query (optional, searches name/email)
    - role: Filter by role name (e.g., 'user', 'accountant')
    - tags: Comma-separated tag IDs for filtering
    - limit: Max results (default: 20)
    - company_id: Company filter (super_admin only)

    Returns:
    - users: Array of matching users with id, name, email, role
    """
    user = get_current_user()
    logger.info(f"GET /search/users - User search by user_id={user.id}")

    query = request.args.get('q', '')
    role_filter = request.args.get('role')
    tags = request.args.get('tags', '')
    limit = request.args.get('limit', 20, type=int)

    # Get company_id
    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id
    logger.debug(f"User search params: query='{query}', role={role_filter}, tags={tags}, limit={limit}")

    # Parse tag IDs
    tag_ids = None
    if tags:
        try:
            tag_ids = [int(t.strip()) for t in tags.split(',') if t.strip()]
            logger.debug(f"Filtering by tag_ids: {tag_ids}")
        except ValueError:
            logger.warning(f"Invalid tag IDs provided: {tags}")
            return error_response('Invalid tag IDs', 400)

    # Get use case and execute search
    use_case = get_search_usecase()
    results = use_case.search_users(
        query=query,
        company_id=company_id,
        role_filter=role_filter,
        tag_ids=tag_ids,
        limit=limit
    )

    logger.info(f"User search completed: {len(results)} results found")
    return success_response({'users': results})


@search_routes_bp.route('/requests', methods=['GET'])
@jwt_required()
@accountant_required
def search_requests():
    """
    Search service requests with advanced filters.

    Performs full-text search on request numbers, descriptions, and
    client names with optional status and assignment filtering.

    Query parameters:
    - q: Search query (optional, searches request_number/description)
    - status: Filter by request status (e.g., 'pending', 'processing')
    - assigned_to: Filter by assigned user ID
    - limit: Max results (default: 20)
    - company_id: Company filter (super_admin only)

    Returns:
    - requests: Array of matching requests with id, request_number, status, client
    """
    user = get_current_user()
    logger.info(f"GET /search/requests - Request search by user_id={user.id}")

    query = request.args.get('q', '')
    status = request.args.get('status')
    assigned_to = request.args.get('assigned_to')
    limit = request.args.get('limit', 20, type=int)

    # Get company_id
    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id
    logger.debug(f"Request search params: query='{query}', status={status}, assigned_to={assigned_to}, limit={limit}")

    # Get use case and execute search
    use_case = get_search_usecase()
    results = use_case.search_requests(
        query=query,
        company_id=company_id,
        status=status,
        assigned_to=assigned_to,
        limit=limit
    )

    logger.info(f"Request search completed: {len(results)} results found")
    return success_response({'requests': results})
