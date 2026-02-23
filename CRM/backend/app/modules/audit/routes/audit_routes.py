"""
Audit Module Routes - Activity Logging and Impersonation API Endpoints

This module provides REST API endpoints for audit logging, activity
tracking, user impersonation (for support), and access log management.

Endpoints:
---------
Activity Logs:
    GET /api/audit/entity/<entity_type>/<entity_id>
        Get activity timeline for a specific entity.
    GET /api/audit/users/<user_id>
        Get activity timeline for a user.
    GET /api/audit
        List activity logs for current company.
    GET /api/audit/search
        Advanced search for activity logs (admin only).

Impersonation (Super Admin Only):
    POST /api/audit/impersonate/<user_id>
        Start impersonating a user.
    POST /api/audit/impersonate/stop
        Stop the current impersonation session.
    GET /api/audit/impersonate/status
        Get current impersonation status.
    GET /api/audit/impersonate/active
        Get active impersonation session.
    GET /api/audit/impersonate/history
        Get impersonation history for audit.
    GET /api/audit/impersonate/user/<user_id>/history
        Get impersonation history for specific user.

Access Logs:
    GET /api/audit/access-logs
        List access logs (login history).
    GET /api/audit/access-logs/<log_id>
        Get detailed access log entry.
    GET /api/audit/access-logs/user/<user_id>
        Get access logs for specific user.
    GET /api/audit/access-logs/suspicious
        Get suspicious access attempts.
    GET /api/audit/access-logs/stats
        Get access statistics.
    GET /api/audit/access-logs/my
        Get current user's own access logs.

Security Notes:
--------------
- Impersonation is logged for compliance and transparency
- Practice owners can view when super admin accessed their accounts
- Suspicious access attempts are flagged for security monitoring
"""
import logging
from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.responses import success_response, error_response, paginated_response
from app.common.decorators import (
    admin_required, accountant_required, get_current_user,
    roles_required, get_impersonation_info
)
from app.modules.audit import audit_bp
from app.modules.audit.usecases import (
    GetEntityActivityUseCase, GetUserActivityUseCase,
    GetCompanyActivityUseCase, SearchActivityUseCase,
    StartImpersonationUseCase, StopImpersonationUseCase,
    GetImpersonationHistoryUseCase, GetMyActiveImpersonationUseCase
)
from app.modules.audit.services import AccessLogger
from app.modules.audit.models import AccessLog

# Module-level logger
logger = logging.getLogger(__name__)


@audit_bp.route('/entity/<entity_type>/<entity_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_entity_activity(entity_type, entity_id):
    """
    Get activity timeline for a specific entity.

    Returns a list of activity log entries showing all actions
    performed on the specified entity.
    """
    logger.info(f"GET /audit/entity/{entity_type}/{entity_id} - Activity request")
    limit = request.args.get('limit', 50, type=int)

    usecase = GetEntityActivityUseCase()
    result = usecase.execute(entity_type, entity_id, limit)

    if result.success:
        logger.debug(f"Retrieved {len(result.data.get('activities', []))} activities for {entity_type}/{entity_id}")
        return success_response(result.data)
    logger.warning(f"Failed to get entity activity: {result.error}")
    return error_response(result.error, 400)


@audit_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_user_activity(user_id):
    """Get activity timeline for a user"""
    limit = request.args.get('limit', 50, type=int)

    usecase = GetUserActivityUseCase()
    result = usecase.execute(user_id, limit)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, 400)


@audit_bp.route('', methods=['GET'])
@jwt_required()
@accountant_required
def list_activities():
    """List activity logs for current company"""
    user = get_current_user()

    # Get company_id
    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id and user.role.name != 'super_admin':
        return error_response('Company ID required', 400)

    # Parse filters
    entity_type = request.args.get('entity_type')
    action = request.args.get('action')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Parse dates
    date_from = None
    date_to = None
    if request.args.get('date_from'):
        try:
            date_from = datetime.fromisoformat(request.args.get('date_from'))
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            date_to = datetime.fromisoformat(request.args.get('date_to'))
        except ValueError:
            pass

    usecase = GetCompanyActivityUseCase()
    result = usecase.execute(
        company_id=company_id,
        entity_type=entity_type,
        action=action,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, 400)


@audit_bp.route('/search', methods=['GET'])
@jwt_required()
@admin_required
def search_activities():
    """Advanced search for activity logs (admin only)"""
    user = get_current_user()

    # Get filters
    company_id = request.args.get('company_id')
    if user.role.name != 'super_admin':
        company_id = user.company_id

    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id')
    action = request.args.get('action')
    performed_by_id = request.args.get('performed_by_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Parse dates
    date_from = None
    date_to = None
    if request.args.get('date_from'):
        try:
            date_from = datetime.fromisoformat(request.args.get('date_from'))
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            date_to = datetime.fromisoformat(request.args.get('date_to'))
        except ValueError:
            pass

    usecase = SearchActivityUseCase()
    result = usecase.execute(
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by_id=performed_by_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, 400)


# ============== Impersonation Routes ==============

def _get_impersonation_status_code(error_code: str) -> int:
    """Map impersonation error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
        'SESSION_ACTIVE': 409,
        'SESSION_ENDED': 400
    }
    return status_map.get(error_code, 400)


@audit_bp.route('/impersonate/<user_id>', methods=['POST'])
@jwt_required()
@roles_required('super_admin')
def start_impersonation(user_id):
    """
    Start impersonating a user (Super Admin only).

    Request body:
    - reason (optional): Reason for impersonation (for audit trail)

    Returns:
    - impersonation_token: Use this token for subsequent requests while impersonating
    - session: Impersonation session details
    - target_user: Details of the user being impersonated
    """
    admin_id = get_jwt_identity()
    reason = request.json.get('reason') if request.json else None

    usecase = StartImpersonationUseCase()
    result = usecase.execute(admin_id, user_id, reason)

    if result.success:
        return success_response(result.data, status_code=201)
    return error_response(result.error, _get_impersonation_status_code(result.error_code))


@audit_bp.route('/impersonate/stop', methods=['POST'])
@jwt_required()
def stop_impersonation():
    """
    Stop the current impersonation session.

    This endpoint can be called with either:
    1. The impersonation token (will extract session_id from claims)
    2. A regular admin token with session_id in the request body

    Returns:
    - access_token: New token for the admin's original identity
    - session: Ended impersonation session details
    """
    impersonation_info = get_impersonation_info()

    if impersonation_info['is_impersonating']:
        # Called with impersonation token
        admin_id = impersonation_info['original_user_id']
        session_id = impersonation_info['session_id']
    else:
        # Called with regular admin token
        admin_id = get_jwt_identity()
        session_id = request.json.get('session_id') if request.json else None

    if not session_id:
        return error_response('No active impersonation session found', 400)

    usecase = StopImpersonationUseCase()
    result = usecase.execute(session_id, admin_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_impersonation_status_code(result.error_code))


@audit_bp.route('/impersonate/status', methods=['GET'])
@jwt_required()
def get_impersonation_status():
    """
    Get current impersonation status.

    Returns whether the current token is an impersonation token
    and details about the session if so.
    """
    impersonation_info = get_impersonation_info()

    if impersonation_info['is_impersonating']:
        from app.modules.audit.models import ImpersonationSession
        session = ImpersonationSession.query.get(impersonation_info['session_id'])
        return success_response({
            'is_impersonating': True,
            'original_user_id': impersonation_info['original_user_id'],
            'impersonated_user_id': impersonation_info['impersonated_user_id'],
            'session': session.to_dict() if session else None
        })

    return success_response({
        'is_impersonating': False,
        'original_user_id': None,
        'impersonated_user_id': None,
        'session': None
    })


@audit_bp.route('/impersonate/active', methods=['GET'])
@jwt_required()
@roles_required('super_admin')
def get_my_active_impersonation():
    """
    Get the current admin's active impersonation session if any.
    """
    admin_id = get_jwt_identity()

    usecase = GetMyActiveImpersonationUseCase()
    result = usecase.execute(admin_id)

    return success_response(result.data)


@audit_bp.route('/impersonate/history', methods=['GET'])
@jwt_required()
@roles_required('super_admin')
def get_impersonation_history():
    """
    Get impersonation history for audit purposes (Super Admin only).

    Query params:
    - admin_id: Filter by admin who performed impersonation
    - target_user_id: Filter by user who was impersonated
    - company_id: Filter by target user's company
    - active_only: Only show active sessions (default: false)
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    """
    admin_id_filter = request.args.get('admin_id')
    target_user_id = request.args.get('target_user_id')
    company_id = request.args.get('company_id')
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    usecase = GetImpersonationHistoryUseCase()
    result = usecase.execute(
        admin_id=admin_id_filter,
        target_user_id=target_user_id,
        company_id=company_id,
        include_active_only=active_only,
        page=page,
        per_page=per_page
    )

    return success_response(result.data)


@audit_bp.route('/impersonate/user/<user_id>/history', methods=['GET'])
@jwt_required()
@admin_required
def get_user_impersonation_history(user_id):
    """
    Get impersonation history for a specific user (visible to practice owners).

    This allows practice owners to see when SuperAdmins accessed their account
    for support purposes (transparency feature).
    """
    current_user = get_current_user()

    # Non-super admins can only view their own company's users
    if current_user.role.name != 'super_admin':
        from app.modules.user.models import User
        target_user = User.query.get(user_id)
        if not target_user or target_user.company_id != current_user.company_id:
            return error_response('Access denied', 403)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    usecase = GetImpersonationHistoryUseCase()
    result = usecase.execute(
        target_user_id=user_id,
        page=page,
        per_page=per_page
    )

    return success_response(result.data)


# ============== Access Logs Routes ==============

@audit_bp.route('/access-logs', methods=['GET'])
@jwt_required()
@admin_required
def list_access_logs():
    """
    List access logs (login history with location and device info).

    Query params:
    - user_id: Filter by specific user
    - access_type: Filter by type (login, logout, failed_login, token_refresh)
    - suspicious_only: Only show suspicious access attempts
    - page: Page number (default: 1)
    - per_page: Items per page (default: 50)
    """
    current_user = get_current_user()

    # Get company_id (super admin can view all or filter by company)
    company_id = request.args.get('company_id')
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    user_id = request.args.get('user_id')
    access_type = request.args.get('access_type')
    suspicious_only = request.args.get('suspicious_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)  # Max 100

    # Build query
    query = AccessLog.query

    if company_id:
        query = query.filter_by(company_id=company_id)

    if user_id:
        query = query.filter_by(user_id=user_id)

    if access_type:
        query = query.filter_by(access_type=access_type)

    if suspicious_only:
        query = query.filter_by(is_suspicious=True)

    # Get total count
    total = query.count()

    # Get paginated results
    logs = query.order_by(AccessLog.created_at.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    return paginated_response(
        [log.to_dict() for log in logs],
        page,
        per_page,
        total
    )


@audit_bp.route('/access-logs/<log_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_access_log(log_id):
    """Get detailed access log entry"""
    current_user = get_current_user()

    log = AccessLog.query.get(log_id)
    if not log:
        return error_response('Access log not found', 404)

    # Check company access
    if current_user.role.name != 'super_admin':
        if log.company_id != current_user.company_id:
            return error_response('Access denied', 403)

    return success_response({'access_log': log.to_dict()})


@audit_bp.route('/access-logs/user/<user_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_user_access_logs(user_id):
    """
    Get access logs for a specific user.

    Query params:
    - limit: Number of logs to return (default: 50, max: 100)
    - include_failed: Include failed login attempts (default: true)
    """
    current_user = get_current_user()

    # Check permission
    from app.modules.user.models import User
    target_user = User.query.get(user_id)
    if not target_user:
        return error_response('User not found', 404)

    # Non-super admins can only view their own company's users
    if current_user.role.name != 'super_admin':
        if target_user.company_id != current_user.company_id:
            return error_response('Access denied', 403)

    limit = min(request.args.get('limit', 50, type=int), 100)
    include_failed = request.args.get('include_failed', 'true').lower() == 'true'

    logs = AccessLogger.get_user_access_logs(user_id, limit, include_failed)

    return success_response({
        'user_id': user_id,
        'user_name': target_user.full_name,
        'access_logs': logs
    })


@audit_bp.route('/access-logs/suspicious', methods=['GET'])
@jwt_required()
@admin_required
def get_suspicious_access_logs():
    """Get suspicious access attempts for security monitoring"""
    current_user = get_current_user()

    company_id = request.args.get('company_id')
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    limit = min(request.args.get('limit', 50, type=int), 100)

    logs = AccessLogger.get_suspicious_access_logs(company_id, limit)

    return success_response({'suspicious_logs': logs})


@audit_bp.route('/access-logs/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_access_stats():
    """
    Get access statistics and analytics.

    Query params:
    - user_id: Filter by specific user
    - days: Time period in days (default: 30, max: 90)
    """
    current_user = get_current_user()

    company_id = request.args.get('company_id')
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    user_id = request.args.get('user_id')
    days = min(request.args.get('days', 30, type=int), 90)

    stats = AccessLogger.get_access_stats(user_id, company_id, days)

    return success_response({'stats': stats})


@audit_bp.route('/access-logs/my', methods=['GET'])
@jwt_required()
def get_my_access_logs():
    """
    Get current user's own access logs.
    This allows users to see their login history for security awareness.
    """
    user_id = get_jwt_identity()
    limit = min(request.args.get('limit', 20, type=int), 50)

    logs = AccessLogger.get_user_access_logs(user_id, limit, include_failed=True)

    return success_response({'access_logs': logs})
