from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt

from app.modules.user.models import User


def get_impersonation_info():
    """
    Get impersonation information from the current JWT token.

    Returns:
        dict with keys:
        - is_impersonating: bool
        - original_user_id: str or None (the super admin doing the impersonation)
        - impersonated_user_id: str or None (the user being impersonated)
        - session_id: str or None (the impersonation session ID)
    """
    try:
        claims = get_jwt()
        return {
            'is_impersonating': claims.get('is_impersonating', False),
            'original_user_id': claims.get('original_user_id'),
            'impersonated_user_id': claims.get('impersonated_user_id'),
            'session_id': claims.get('impersonation_session_id')
        }
    except Exception:
        return {
            'is_impersonating': False,
            'original_user_id': None,
            'impersonated_user_id': None,
            'session_id': None
        }


def get_original_admin():
    """
    Get the original super admin user if currently impersonating.

    Returns:
        User object of the super admin, or None if not impersonating
    """
    info = get_impersonation_info()
    if info['is_impersonating'] and info['original_user_id']:
        return User.query.get(info['original_user_id'])
    return None


def roles_required(*allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Usage: @roles_required('super_admin', 'admin')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403

            if user.role.name not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'Required role: {", ".join(allowed_roles)}'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator for routes that require admin, senior_accountant, or super_admin access"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        if user.role.name not in ['super_admin', 'admin', 'senior_accountant']:
            return jsonify({'error': 'Admin access required'}), 403

        return fn(*args, **kwargs)
    return wrapper


def super_admin_required(fn):
    """Decorator for routes that require super_admin access only"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        if user.role.name != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403

        return fn(*args, **kwargs)
    return wrapper


def accountant_required(fn):
    """Decorator for routes that require accountant, senior_accountant, admin, or super_admin access"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        if user.role.name not in ['super_admin', 'admin', 'senior_accountant', 'accountant']:
            return jsonify({'error': 'Accountant access required'}), 403

        return fn(*args, **kwargs)
    return wrapper


def invoice_admin_required(fn):
    """Decorator for invoice routes - requires admin or super_admin access (excludes senior_accountant)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        if user.role.name not in ['super_admin', 'admin', 'accountant']:
            return jsonify({'error': 'Invoice management access required'}), 403

        return fn(*args, **kwargs)
    return wrapper


def senior_accountant_required(fn):
    """Decorator for routes that require senior_accountant, admin, or super_admin access"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        if user.role.name not in ['super_admin', 'admin', 'senior_accountant']:
            return jsonify({'error': 'Senior accountant access required'}), 403

        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Helper function to get the current authenticated user"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def plan_feature_required(feature_name):
    """
    Decorator to restrict access based on plan features.

    Usage:
        @plan_feature_required('bulk_email')
        def send_bulk_emails():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Super admins bypass feature checks
            if user.role.name == 'super_admin':
                return fn(*args, **kwargs)

            if not user.company_id:
                return jsonify({
                    'error': 'This feature requires a company account'
                }), 403

            from app.modules.company.services import PlanLimitService
            has_feature, error_msg = PlanLimitService.check_feature(user.company_id, feature_name)

            if not has_feature:
                return jsonify({
                    'error': error_msg,
                    'error_code': 'PLAN_FEATURE_UNAVAILABLE',
                    'feature': feature_name
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def plan_limit_check(limit_type):
    """
    Decorator to check plan limits before allowing an action.

    Usage:
        @plan_limit_check('user')  # For adding users/staff
        @plan_limit_check('client')  # For adding clients
        @plan_limit_check('service')  # For activating services
        @plan_limit_check('form')  # For creating forms
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Super admins bypass limit checks
            if user.role.name == 'super_admin':
                return fn(*args, **kwargs)

            if not user.company_id:
                return jsonify({
                    'error': 'This action requires a company account'
                }), 403

            from app.modules.company.services import PlanLimitService

            can_proceed = True
            error_msg = None

            if limit_type == 'user':
                # Get the role from request to determine user vs client
                role_name = None
                if hasattr(kwargs, 'get'):
                    role_name = kwargs.get('role')
                from flask import request
                if request.json:
                    role_name = request.json.get('role', 'user')
                can_proceed, error_msg = PlanLimitService.can_add_user(user.company_id, role_name or 'accountant')

            elif limit_type == 'client':
                can_proceed, error_msg = PlanLimitService.can_add_user(user.company_id, 'user')

            elif limit_type == 'service':
                can_proceed, error_msg = PlanLimitService.can_add_service(user.company_id)

            elif limit_type == 'form':
                can_proceed, error_msg = PlanLimitService.can_create_form(user.company_id)

            if not can_proceed:
                return jsonify({
                    'error': error_msg,
                    'error_code': 'PLAN_LIMIT_EXCEEDED',
                    'limit_type': limit_type
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
