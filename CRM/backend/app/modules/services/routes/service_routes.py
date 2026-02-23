"""
Service Catalog Routes - Thin Controllers

These routes handle HTTP concerns and delegate business logic to use cases.
"""
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError

from . import services_bp
from app.modules.services.usecases import (
    CreateServiceUseCase,
    UpdateServiceUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
    ListDefaultServicesUseCase,
    GetCompanyServiceSettingsUseCase,
    ActivateServiceForCompanyUseCase,
    UpdateCompanyServiceSettingsUseCase,
    BulkActivateServicesUseCase,
    ListServicesForCompanyUseCase,
)
from app.modules.services.schemas import (
    CreateServiceSchema,
    UpdateServiceSchema,
    UpdateCompanyServiceSettingsSchema,
    BulkServiceActivationSchema,
)
from app.common.decorators import admin_required, get_current_user
from app.common.responses import success_response, error_response


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
        'INVALID_ROLE': 400,
        'INVALID_STATUS': 400,
        'DUPLICATE_NAME': 400,
        'INVALID_SERVICE': 400,
        'NO_COMPANY': 400,
    }
    return status_map.get(error_code, 400)


# ============== Service Catalog Routes ==============

@services_bp.route('/', methods=['GET'])
@jwt_required()
def list_services():
    """List all services (filtered by company type for non-super-admin users)"""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    category = request.args.get('category')
    user_id = get_jwt_identity()

    usecase = ListServicesUseCase()
    result = usecase.execute(active_only, category, user_id)

    return success_response(result.data)


@services_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_service():
    """Create a new service (Admin only)"""
    try:
        schema = CreateServiceSchema()
        data = schema.load(request.json)

        usecase = CreateServiceUseCase()
        result = usecase.execute(
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            base_price=data.get('base_price'),
            form_id=data.get('form_id'),
            workflow_id=data.get('workflow_id'),
            cost_percentage=data.get('cost_percentage'),
            cost_category=data.get('cost_category')
        )

        if result.success:
            return success_response(result.data, message='Service created successfully', status_code=201)
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@services_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service(service_id):
    """Get a service by ID"""
    usecase = GetServiceUseCase()
    result = usecase.execute(service_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@services_bp.route('/<int:service_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_service(service_id):
    """Update a service (Admin only)"""
    try:
        schema = UpdateServiceSchema()
        data = schema.load(request.json)

        usecase = UpdateServiceUseCase()
        result = usecase.execute(service_id, data)

        if result.success:
            return success_response(result.data, message='Service updated successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


# ============== Company Service Settings Routes ==============

@services_bp.route('/defaults', methods=['GET'])
@jwt_required()
@admin_required
def list_default_services():
    """List all default services with company activation status (Admin only)"""
    user_id = get_jwt_identity()

    usecase = ListDefaultServicesUseCase()
    result = usecase.execute(user_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@services_bp.route('/defaults/<int:service_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_default_service_settings(service_id):
    """Get company-specific settings for a default service"""
    user_id = get_jwt_identity()

    usecase = GetCompanyServiceSettingsUseCase()
    result = usecase.execute(service_id, user_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@services_bp.route('/defaults/<int:service_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_default_service(service_id):
    """Activate a default service for the company"""
    user_id = get_jwt_identity()

    usecase = ActivateServiceForCompanyUseCase()
    result = usecase.execute(service_id, user_id, is_active=True)

    if result.success:
        return success_response(result.data, message='Service activated successfully')
    return error_response(result.error, _get_status_code(result.error_code))


@services_bp.route('/defaults/<int:service_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def deactivate_default_service(service_id):
    """Deactivate a default service for the company"""
    user_id = get_jwt_identity()

    usecase = ActivateServiceForCompanyUseCase()
    result = usecase.execute(service_id, user_id, is_active=False)

    if result.success:
        return success_response(result.data, message='Service deactivated successfully')
    return error_response(result.error, _get_status_code(result.error_code))


@services_bp.route('/defaults/<int:service_id>/settings', methods=['PATCH'])
@jwt_required()
@admin_required
def update_default_service_settings(service_id):
    """Update company-specific settings for a default service"""
    try:
        user_id = get_jwt_identity()
        schema = UpdateCompanyServiceSettingsSchema()
        data = schema.load(request.json)

        usecase = UpdateCompanyServiceSettingsUseCase()
        result = usecase.execute(service_id, user_id, data)

        if result.success:
            return success_response(result.data, message='Service settings updated successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@services_bp.route('/defaults/bulk-activate', methods=['POST'])
@jwt_required()
@admin_required
def bulk_activate_services():
    """Bulk activate multiple default services for the company"""
    try:
        user_id = get_jwt_identity()
        schema = BulkServiceActivationSchema()
        data = schema.load(request.json)

        usecase = BulkActivateServicesUseCase()
        result = usecase.execute(data['service_ids'], user_id, data['is_active'])

        if result.success:
            return success_response(result.data)
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@services_bp.route('/available', methods=['GET'])
@jwt_required()
def list_available_services():
    """List services available to the current user's company"""
    user_id = get_jwt_identity()
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    # Only admins can see inactive services
    current_user = get_current_user()
    if include_inactive and current_user.role.name not in ['super_admin', 'admin']:
        include_inactive = False

    usecase = ListServicesForCompanyUseCase()
    result = usecase.execute(user_id, include_inactive=include_inactive)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))
