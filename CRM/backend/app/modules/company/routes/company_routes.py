"""
Company Routes - API Endpoints
==============================

This module provides thin controllers that handle HTTP concerns and delegate
business logic to use cases. Following Clean Architecture principles, routes:

1. Parse and validate HTTP requests
2. Extract authentication/authorization info
3. Call appropriate use cases
4. Format HTTP responses

Routes DO NOT contain business logic - that's in usecases.py.

Endpoints:
---------
Company CRUD:
    POST   /companies              - Create new company (Super Admin)
    GET    /companies              - List all companies (Super Admin)
    GET    /companies/<id>         - Get company details
    PUT    /companies/<id>         - Update company
    DELETE /companies/<id>         - Deactivate company (Super Admin)

Company Users:
    GET    /companies/<id>/users   - List company users
    POST   /companies/<id>/users   - Add user to company

Company Contacts:
    GET    /companies/<id>/contacts         - List contacts
    POST   /companies/<id>/contacts         - Add contact
    PUT    /companies/<id>/contacts/<id>    - Update contact
    DELETE /companies/<id>/contacts/<id>    - Delete contact

Configuration:
    GET/PUT /companies/<id>/email-config    - Email SMTP config
    GET/PUT /companies/<id>/storage-config  - Storage provider config
    GET/PUT /companies/<id>/currency-settings - Currency/tax settings

Author: CRM Development Team
"""

import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.modules.company import company_bp
from app.modules.company.models import (
    CompanyEmailConfig, CompanyStorageConfig, SystemEmailConfig,
    EmailProviderType, StorageProviderType
)
from app.extensions import db
from app.modules.company.usecases import (
    CreateCompanyUseCase,
    UpdateCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    DeleteCompanyUseCase,
    AddUserToCompanyUseCase,
    GetCompanyUsersUseCase,
    TransferOwnershipUseCase,
    GetMyCompanyUseCase,
    # Company Contact Use Cases
    ListCompanyContactsUseCase,
    GetCompanyContactHistoryUseCase,
    AddCompanyContactUseCase,
    UpdateCompanyContactUseCase,
    DeleteCompanyContactUseCase,
    SetPrimaryContactUseCase
)
from app.modules.user.models import User, Role

# Configure module-level logger
logger = logging.getLogger(__name__)


def _check_super_admin(user_id: str) -> tuple:
    """
    Helper function to verify if the current user has super admin privileges.

    Args:
        user_id: The ID of the user to check

    Returns:
        tuple: (is_admin: bool, error_response: Response or None, status_code: int or None)

    Usage:
        is_admin, error_response, status = _check_super_admin(user_id)
        if not is_admin:
            return error_response, status
    """
    logger.debug(f"Checking super admin status for user_id={user_id}")
    user = User.query.get(user_id)

    if not user:
        logger.warning(f"User not found during admin check: user_id={user_id}")
        return False, jsonify({
            'success': False,
            'error': 'User not found. Please login again.'
        }), 401

    if user.role.name != Role.SUPER_ADMIN:
        logger.warning(f"Non-admin user attempted admin action: user_id={user_id}, role={user.role.name}")
        return False, jsonify({
            'success': False,
            'error': 'Only super admin can perform this action'
        }), 403

    logger.debug(f"Super admin check passed for user_id={user_id}")
    return True, None, None


@company_bp.route('', methods=['POST'])
@jwt_required()
def create_company():
    """
    Create a new company/practice with owner (Super Admin only).

    This endpoint creates a new accounting practice/company along with
    an admin user who will be the practice owner. A welcome email with
    temporary credentials is sent to the owner.

    Request Body:
        - name (required): Company legal name
        - owner_email (required): Email for the practice owner
        - owner_first_name: Owner's first name
        - owner_last_name: Owner's last name
        - trading_name: Business trading name if different
        - abn: Australian Business Number
        - plan_type: 'starter', 'standard', 'premium', 'enterprise'

    Returns:
        201: Company created successfully with owner details
        400: Validation error or email already exists
        403: Not a super admin
    """
    user_id = get_jwt_identity()
    logger.info(f"POST /companies - Create company request by user_id={user_id}")

    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    data = request.get_json()
    logger.debug(f"Creating company with data: name={data.get('name')}, owner_email={data.get('owner_email')}")

    usecase = CreateCompanyUseCase()
    result = usecase.execute(data, user_id)

    if result.success:
        logger.info(f"Company created successfully: company_id={result.data.get('company', {}).get('id')}")
        return jsonify({
            'success': True,
            **result.data
        }), 201
    else:
        logger.warning(f"Company creation failed: {result.error} (code={result.error_code})")
        status_code = 400 if result.error_code in ['VALIDATION_ERROR', 'EMAIL_EXISTS'] else 500
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('', methods=['GET'])
@jwt_required()
def list_companies():
    """List all companies (Super Admin only)"""
    user_id = get_jwt_identity()

    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search')
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    usecase = ListCompaniesUseCase()
    result = usecase.execute(
        page=page,
        per_page=per_page,
        search=search,
        active_only=active_only
    )

    return jsonify({
        'success': True,
        **result.data
    })


@company_bp.route('/<company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Get company details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found. Please login again.'}), 401

    usecase = GetCompanyUseCase()
    result = usecase.execute(company_id, include_owner=True, include_stats=True)

    if not result.success:
        return jsonify({'success': False, 'error': result.error}), 404

    # Check permission - super admin, company owner, or company member
    company = result.data['company']
    if user.role.name != Role.SUPER_ADMIN:
        if user.company_id != company_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

    return jsonify({
        'success': True,
        **result.data
    })


@company_bp.route('/<company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id):
    """Update company details"""
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = UpdateCompanyUseCase()
    result = usecase.execute(company_id, data, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    """Delete (deactivate) a company (Super Admin only)"""
    user_id = get_jwt_identity()

    usecase = DeleteCompanyUseCase()
    result = usecase.execute(company_id, user_id)

    if result.success:
        return jsonify({'success': True, 'message': 'Company deactivated'})
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/users', methods=['GET'])
@jwt_required()
def get_company_users(company_id):
    """Get users in a company"""
    user_id = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role_filter = request.args.get('role')

    usecase = GetCompanyUsersUseCase()
    result = usecase.execute(company_id, user_id, role_filter, page, per_page)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/users', methods=['POST'])
@jwt_required()
def add_company_user(company_id):
    """Add a user to a company"""
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = AddUserToCompanyUseCase()
    result = usecase.execute(company_id, data, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        }), 201
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else \
                      409 if result.error_code == 'EMAIL_EXISTS' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/transfer-ownership', methods=['POST'])
@jwt_required()
def transfer_ownership(company_id):
    """Transfer company ownership to another user"""
    user_id = get_jwt_identity()
    data = request.get_json()

    new_owner_id = data.get('new_owner_id')
    if not new_owner_id:
        return jsonify({
            'success': False,
            'error': 'new_owner_id is required'
        }), 400

    usecase = TransferOwnershipUseCase()
    result = usecase.execute(company_id, new_owner_id, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/my-company', methods=['GET'])
@jwt_required()
def get_my_company():
    """Get the current user's company"""
    user_id = get_jwt_identity()

    usecase = GetMyCompanyUseCase()
    result = usecase.execute(user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        return jsonify({'success': False, 'error': result.error}), 404


@company_bp.route('/my-company/logo', methods=['POST'])
@jwt_required()
def upload_company_logo():
    """Upload company logo (Admin only) - stores in database"""
    from werkzeug.utils import secure_filename
    from app.modules.company.models import Company
    from app.extensions import db
    import os

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    # Only admins can upload company logo
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Only admins can upload company logo'}), 403

    if not user.company_id:
        return jsonify({'success': False, 'error': 'No company associated with user'}), 404

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # Validate file type (images only)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext not in allowed_extensions:
        return jsonify({
            'success': False,
            'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
        }), 400

    # Check file size (max 2MB for database storage)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > 2 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'File size must be less than 2MB'}), 400

    try:
        # Read file data
        file_data = file.read()

        # Determine MIME type
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml'
        }
        mime_type = mime_types.get(ext, 'image/png')

        # Update company with logo data
        company = Company.query.get(user.company_id)
        if company:
            company.logo_data = file_data
            company.logo_mime_type = mime_type
            # Set logo_url to point to our serve endpoint
            company.logo_url = f'/api/companies/{user.company_id}/logo/image'
            db.session.commit()

        return jsonify({
            'success': True,
            'logo_url': f'/api/companies/{user.company_id}/logo/image',
            'message': 'Logo uploaded successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to upload logo: {str(e)}'}), 500


@company_bp.route('/<company_id>/logo/image', methods=['GET'])
def serve_company_logo(company_id):
    """Serve company logo image from database (public endpoint)"""
    from flask import Response
    from app.modules.company.models import Company

    company = Company.query.get(company_id)

    if not company or not company.logo_data:
        # Return a 1x1 transparent pixel as fallback
        transparent_pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        return Response(transparent_pixel, mimetype='image/png')

    return Response(
        company.logo_data,
        mimetype=company.logo_mime_type or 'image/png',
        headers={
            'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
            'Content-Disposition': 'inline'
        }
    )


@company_bp.route('/my-company/logo', methods=['DELETE'])
@jwt_required()
def delete_company_logo():
    """Delete company logo (Admin only)"""
    from app.modules.company.models import Company
    from app.extensions import db

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Only admins can delete company logo'}), 403

    if not user.company_id:
        return jsonify({'success': False, 'error': 'No company associated with user'}), 404

    company = Company.query.get(user.company_id)
    if company:
        company.logo_url = None
        company.logo_data = None
        company.logo_mime_type = None
        db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Logo deleted successfully'
    })


@company_bp.route('/<company_id>/logo', methods=['POST'])
@jwt_required()
def upload_company_logo_by_id(company_id):
    """Upload company logo for a specific company (Super Admin only) - stores in database"""
    from app.modules.company.models import Company
    from app.extensions import db

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    # Only super admins can upload logo for other companies
    if user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Only super admins can upload logos for other companies'}), 403

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # Validate file type
    allowed_types = {'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'}
    if file.content_type not in allowed_types:
        return jsonify({'success': False, 'error': 'Invalid file type. Allowed: PNG, JPG, GIF, WebP, SVG'}), 400

    # Check file size (max 2MB for database storage)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > 2 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'File size must be less than 2MB'}), 400

    try:
        # Read file data
        file_data = file.read()

        # Use content type from file
        mime_type = file.content_type

        # Update company with logo data
        company.logo_data = file_data
        company.logo_mime_type = mime_type
        company.logo_url = f'/api/companies/{company_id}/logo/image'
        db.session.commit()

        return jsonify({
            'success': True,
            'logo_url': f'/api/companies/{company_id}/logo/image',
            'message': 'Logo uploaded successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to upload logo: {str(e)}'}), 500


@company_bp.route('/<company_id>/logo', methods=['DELETE'])
@jwt_required()
def delete_company_logo_by_id(company_id):
    """Delete company logo for a specific company (Super Admin only)"""
    from app.modules.company.models import Company
    from app.extensions import db

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    # Only super admins can delete logo for other companies
    if user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Only super admins can delete logos for other companies'}), 403

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404

    company.logo_url = None
    company.logo_data = None
    company.logo_mime_type = None
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Logo deleted successfully'
    })


# ============== Plan & Usage Routes ==============

@company_bp.route('/my-company/usage', methods=['GET'])
@jwt_required()
def get_my_company_usage():
    """
    Get plan usage statistics for the current user's company.

    Returns current usage vs limits for:
    - Users (staff members)
    - Clients
    - Services
    - Forms
    - Available features
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    if not user.company_id:
        return jsonify({'success': False, 'error': 'No company associated with user'}), 404

    from app.modules.company.services import PlanLimitService

    stats = PlanLimitService.get_usage_stats(user.company_id)
    if not stats:
        return jsonify({'success': False, 'error': 'Failed to get usage stats'}), 500

    return jsonify({
        'success': True,
        'usage': stats
    })


@company_bp.route('/<company_id>/usage', methods=['GET'])
@jwt_required()
def get_company_usage(company_id):
    """
    Get plan usage statistics for a specific company (Super Admin or company members).
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    # Check permission
    if user.role.name != Role.SUPER_ADMIN and user.company_id != company_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    from app.modules.company.services import PlanLimitService

    stats = PlanLimitService.get_usage_stats(company_id)
    if not stats:
        return jsonify({'success': False, 'error': 'Company not found'}), 404

    return jsonify({
        'success': True,
        'usage': stats
    })


@company_bp.route('/<company_id>/plan', methods=['PATCH'])
@jwt_required()
def update_company_plan(company_id):
    """
    Update company plan (Super Admin only).

    Request body:
    - plan_type: 'starter', 'standard', 'premium', 'enterprise'
    - max_users: (optional) override maximum users
    - max_clients: (optional) override maximum clients
    """
    user_id = get_jwt_identity()

    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    from app.modules.company.models import Company
    from app.modules.company.services import PLAN_LIMITS

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404

    data = request.get_json()

    # Update plan type
    if 'plan_type' in data:
        if data['plan_type'] not in PLAN_LIMITS:
            return jsonify({
                'success': False,
                'error': f"Invalid plan type. Must be one of: {', '.join(PLAN_LIMITS.keys())}"
            }), 400
        company.plan_type = data['plan_type']

    # Update overrides (must be >= plan defaults)
    plan_defaults = PLAN_LIMITS.get(company.plan_type, PLAN_LIMITS['standard'])

    if 'max_users' in data:
        if data['max_users'] < plan_defaults['max_users'] and plan_defaults['max_users'] != -1:
            return jsonify({
                'success': False,
                'error': f"max_users cannot be less than plan default ({plan_defaults['max_users']})"
            }), 400
        company.max_users = data['max_users']

    if 'max_clients' in data:
        if data['max_clients'] < plan_defaults['max_clients'] and plan_defaults['max_clients'] != -1:
            return jsonify({
                'success': False,
                'error': f"max_clients cannot be less than plan default ({plan_defaults['max_clients']})"
            }), 400
        company.max_clients = data['max_clients']

    from app.extensions import db
    db.session.commit()

    return jsonify({
        'success': True,
        'company': company.to_dict(include_stats=True),
        'message': f"Plan updated to {company.plan_type}"
    })


@company_bp.route('/plans', methods=['GET'])
@jwt_required()
def list_available_plans():
    """
    List all available plans with their limits and features.
    """
    from app.modules.company.services import PLAN_LIMITS

    plans = []
    for plan_name, limits in PLAN_LIMITS.items():
        plans.append({
            'name': plan_name,
            'limits': {
                'max_users': limits['max_users'],
                'max_clients': limits['max_clients'],
                'max_services': limits['max_services'],
                'max_forms': limits['max_forms'],
                'max_storage_mb': limits['max_storage_mb']
            },
            'features': limits['features']
        })

    return jsonify({
        'success': True,
        'plans': plans
    })


# ============== Currency & Tax Configuration Routes ==============

@company_bp.route('/currencies', methods=['GET'])
@jwt_required()
def list_currencies():
    """
    List all supported currencies from database.

    Returns list of currencies with:
    - code: ISO 4217 currency code (AUD, USD, GBP, etc.)
    - symbol: Currency symbol ($, etc.)
    - name: Full currency name
    """
    from app.modules.company.models import Currency

    currencies = Currency.query.filter_by(is_active=True).order_by(Currency.code).all()

    return jsonify({
        'success': True,
        'currencies': [c.to_dict() for c in currencies]
    })


@company_bp.route('/currencies', methods=['POST'])
@jwt_required()
def create_currency():
    """Create a new currency (Super Admin only)"""
    from app.modules.company.models import Currency
    from app.extensions import db

    user_id = get_jwt_identity()
    is_admin, error_response, status_code = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status_code

    data = request.get_json()

    if not all(k in data for k in ['code', 'name', 'symbol']):
        return jsonify({'success': False, 'error': 'code, name, and symbol are required'}), 400

    if Currency.query.filter_by(code=data['code'].upper()).first():
        return jsonify({'success': False, 'error': 'Currency code already exists'}), 400

    currency = Currency(
        code=data['code'].upper(),
        name=data['name'],
        symbol=data['symbol'],
        is_active=data.get('is_active', True)
    )
    db.session.add(currency)
    db.session.commit()

    return jsonify({
        'success': True,
        'currency': currency.to_dict(),
        'message': f'Currency {currency.code} created'
    }), 201


@company_bp.route('/currencies/<int:currency_id>', methods=['PUT'])
@jwt_required()
def update_currency(currency_id):
    """Update a currency (Super Admin only)"""
    from app.modules.company.models import Currency
    from app.extensions import db

    user_id = get_jwt_identity()
    is_admin, error_response, status_code = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status_code

    currency = Currency.query.get(currency_id)
    if not currency:
        return jsonify({'success': False, 'error': 'Currency not found'}), 404

    data = request.get_json()

    if 'name' in data:
        currency.name = data['name']
    if 'symbol' in data:
        currency.symbol = data['symbol']
    if 'is_active' in data:
        currency.is_active = data['is_active']

    db.session.commit()

    return jsonify({
        'success': True,
        'currency': currency.to_dict(),
        'message': f'Currency {currency.code} updated'
    })


@company_bp.route('/currencies/<int:currency_id>', methods=['DELETE'])
@jwt_required()
def delete_currency(currency_id):
    """Delete a currency (Super Admin only) - soft delete by setting is_active=False"""
    from app.modules.company.models import Currency
    from app.extensions import db

    user_id = get_jwt_identity()
    is_admin, error_response, status_code = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status_code

    currency = Currency.query.get(currency_id)
    if not currency:
        return jsonify({'success': False, 'error': 'Currency not found'}), 404

    currency.is_active = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Currency {currency.code} deactivated'
    })


@company_bp.route('/tax-types', methods=['GET'])
@jwt_required()
def list_tax_types():
    """List all supported tax types from database."""
    from app.modules.company.models import TaxType

    tax_types = TaxType.query.filter_by(is_active=True).order_by(TaxType.code).all()

    return jsonify({
        'success': True,
        'tax_types': [t.to_dict() for t in tax_types]
    })


@company_bp.route('/tax-types', methods=['POST'])
@jwt_required()
def create_tax_type():
    """Create a new tax type (Super Admin only)"""
    from app.modules.company.models import TaxType
    from app.extensions import db

    user_id = get_jwt_identity()
    is_admin, error_response, status_code = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status_code

    data = request.get_json()

    if not all(k in data for k in ['code', 'name']):
        return jsonify({'success': False, 'error': 'code and name are required'}), 400

    if TaxType.query.filter_by(code=data['code'].upper()).first():
        return jsonify({'success': False, 'error': 'Tax type code already exists'}), 400

    tax_type = TaxType(
        code=data['code'].upper(),
        name=data['name'],
        default_rate=data.get('default_rate', 0),
        is_active=data.get('is_active', True)
    )
    db.session.add(tax_type)
    db.session.commit()

    return jsonify({
        'success': True,
        'tax_type': tax_type.to_dict(),
        'message': f'Tax type {tax_type.code} created'
    }), 201


@company_bp.route('/tax-types/<int:tax_type_id>', methods=['PUT'])
@jwt_required()
def update_tax_type(tax_type_id):
    """Update a tax type (Super Admin only)"""
    from app.modules.company.models import TaxType
    from app.extensions import db

    user_id = get_jwt_identity()
    is_admin, error_response, status_code = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status_code

    tax_type = TaxType.query.get(tax_type_id)
    if not tax_type:
        return jsonify({'success': False, 'error': 'Tax type not found'}), 404

    data = request.get_json()

    if 'name' in data:
        tax_type.name = data['name']
    if 'default_rate' in data:
        tax_type.default_rate = data['default_rate']
    if 'is_active' in data:
        tax_type.is_active = data['is_active']

    db.session.commit()

    return jsonify({
        'success': True,
        'tax_type': tax_type.to_dict(),
        'message': f'Tax type {tax_type.code} updated'
    })


@company_bp.route('/tax-types/<int:tax_type_id>', methods=['DELETE'])
@jwt_required()
def delete_tax_type(tax_type_id):
    """Delete a tax type (Super Admin only) - soft delete by setting is_active=False"""
    from app.modules.company.models import TaxType
    from app.extensions import db

    user_id = get_jwt_identity()
    is_admin, error_response, status_code = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status_code

    tax_type = TaxType.query.get(tax_type_id)
    if not tax_type:
        return jsonify({'success': False, 'error': 'Tax type not found'}), 404

    tax_type.is_active = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Tax type {tax_type.code} deactivated'
    })


@company_bp.route('/<company_id>/currency-settings', methods=['PUT'])
@jwt_required()
def update_currency_settings(company_id):
    """
    Update currency and tax settings for a company.
    Super Admin can update any company. Admin can update own company.

    Request body:
    - currency: ISO 4217 currency code
    - currency_symbol: (optional) custom symbol
    - tax_type: GST, VAT, Sales Tax, or none
    - tax_label: (optional) custom label (e.g., "GST", "VAT", "Sales Tax")
    - default_tax_rate: (optional) percentage rate
    """
    from app.modules.company.models import Company
    from app.extensions import db

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    # Permission check - Super Admin or company Admin
    if user.role.name == Role.SUPER_ADMIN:
        pass  # Super admin can update any company
    elif user.role.name == Role.ADMIN and user.company_id == company_id:
        pass  # Admin can update their own company
    else:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'error': 'Company not found'}), 404

    data = request.get_json()

    # Update currency
    if 'currency' in data:
        currency = data['currency'].upper()
        company.currency = currency
        # Auto-set symbol if not provided
        if 'currency_symbol' not in data:
            company.currency_symbol = Company.get_currency_symbol(currency)

    if 'currency_symbol' in data:
        company.currency_symbol = data['currency_symbol']

    # Update tax type
    if 'tax_type' in data:
        tax_type = data['tax_type']
        if tax_type not in [Company.TAX_GST, Company.TAX_VAT, Company.TAX_SALES_TAX, Company.TAX_NONE]:
            return jsonify({
                'success': False,
                'error': f'Invalid tax type. Must be: {Company.TAX_GST}, {Company.TAX_VAT}, {Company.TAX_SALES_TAX}, or {Company.TAX_NONE}'
            }), 400
        company.tax_type = tax_type
        # Auto-set label if not provided
        if 'tax_label' not in data:
            company.tax_label = tax_type if tax_type != 'none' else 'Tax'

    if 'tax_label' in data:
        company.tax_label = data['tax_label']

    if 'default_tax_rate' in data:
        rate = float(data['default_tax_rate'])
        if rate < 0 or rate > 100:
            return jsonify({
                'success': False,
                'error': 'Tax rate must be between 0 and 100'
            }), 400
        company.default_tax_rate = rate

    db.session.commit()

    return jsonify({
        'success': True,
        'company': company.to_dict(),
        'message': 'Currency and tax settings updated'
    })


@company_bp.route('/my-company/currency-settings', methods=['PUT'])
@jwt_required()
def update_my_company_currency_settings():
    """
    Update currency and tax settings for the current user's company.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401

    if not user.company_id:
        return jsonify({'success': False, 'error': 'No company associated with user'}), 404

    # Only admins can update currency settings
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Only admins can update currency settings'}), 403

    # Delegate to the general endpoint
    return update_currency_settings(user.company_id)


# ============== Company Contacts Routes ==============

@company_bp.route('/<company_id>/contacts', methods=['GET'])
@jwt_required()
def list_company_contacts(company_id):
    """
    List all active contacts for a company.

    Query params:
    - include_inactive: 'true' to include inactive contacts (default: false)
    """
    user_id = get_jwt_identity()

    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    usecase = ListCompanyContactsUseCase()
    result = usecase.execute(company_id, user_id, include_inactive)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/contacts/history', methods=['GET'])
@jwt_required()
def get_company_contacts_history(company_id):
    """
    Get all contacts for a company including historical (inactive) ones.
    """
    user_id = get_jwt_identity()

    usecase = GetCompanyContactHistoryUseCase()
    result = usecase.execute(company_id, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/contacts', methods=['POST'])
@jwt_required()
def add_company_contact(company_id):
    """
    Add a new contact to a company.

    Request body:
    - first_name: (required) Contact's first name
    - last_name: (required) Contact's last name
    - email: Contact's email address
    - phone: Contact's phone number
    - position: Job title/position
    - contact_type: PRIMARY, BILLING, TECHNICAL, COMPLIANCE, or OTHER
    - is_primary: Whether this is the primary contact
    - effective_from: Date from which contact is effective (YYYY-MM-DD)
    - effective_to: Date until which contact is effective (YYYY-MM-DD)
    - notes: Additional notes
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = AddCompanyContactUseCase()
    result = usecase.execute(company_id, data, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        }), 201
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/contacts/<contact_id>', methods=['PUT'])
@jwt_required()
def update_company_contact(company_id, contact_id):
    """
    Update an existing contact.

    Request body (all fields optional):
    - first_name: Contact's first name
    - last_name: Contact's last name
    - email: Contact's email address
    - phone: Contact's phone number
    - position: Job title/position
    - contact_type: PRIMARY, BILLING, TECHNICAL, COMPLIANCE, or OTHER
    - is_primary: Whether this is the primary contact
    - effective_from: Date from which contact is effective (YYYY-MM-DD)
    - effective_to: Date until which contact is effective (YYYY-MM-DD)
    - is_active: Whether contact is active
    - notes: Additional notes
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    usecase = UpdateCompanyContactUseCase()
    result = usecase.execute(company_id, contact_id, data, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/contacts/<contact_id>', methods=['DELETE'])
@jwt_required()
def delete_company_contact(company_id, contact_id):
    """
    Soft delete a contact (sets effective_to date and is_active to False).
    """
    user_id = get_jwt_identity()

    usecase = DeleteCompanyContactUseCase()
    result = usecase.execute(company_id, contact_id, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


@company_bp.route('/<company_id>/contacts/<contact_id>/set-primary', methods=['PUT'])
@jwt_required()
def set_primary_company_contact(company_id, contact_id):
    """
    Set a contact as the primary contact for the company.
    """
    user_id = get_jwt_identity()

    usecase = SetPrimaryContactUseCase()
    result = usecase.execute(company_id, contact_id, user_id)

    if result.success:
        return jsonify({
            'success': True,
            **result.data
        })
    else:
        status_code = 404 if result.error_code == 'NOT_FOUND' else \
                      403 if result.error_code == 'FORBIDDEN' else 400
        return jsonify({'success': False, 'error': result.error}), status_code


# ============== Company Email Configuration Routes ==============

@company_bp.route('/<company_id>/email-config', methods=['GET'])
@jwt_required()
def get_company_email_config(company_id):
    """Get company SMTP email configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission - company owner, admin, or super admin
    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyEmailConfig.query.filter_by(company_id=company_id).first()

    return jsonify({
        'success': True,
        'config': config.to_dict() if config else None,
        'provider_options': [{'value': p.value, 'label': p.value.title()} for p in EmailProviderType],
        'provider_settings': CompanyEmailConfig.PROVIDER_SETTINGS
    })


@company_bp.route('/<company_id>/email-config', methods=['PUT'])
@jwt_required()
def update_company_email_config(company_id):
    """Update company SMTP email configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission - company owner, admin, or super admin
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Only admins can update email configuration'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    data = request.get_json()

    # Get or create config
    config = CompanyEmailConfig.query.filter_by(company_id=company_id).first()
    if not config:
        import uuid
        config = CompanyEmailConfig(id=str(uuid.uuid4()), company_id=company_id)
        db.session.add(config)

    # Update fields
    if 'provider' in data:
        try:
            config.provider = EmailProviderType(data['provider'])
            # Auto-fill provider settings
            if config.provider.value in CompanyEmailConfig.PROVIDER_SETTINGS:
                settings = CompanyEmailConfig.PROVIDER_SETTINGS[config.provider.value]
                config.smtp_host = settings['smtp_host']
                config.smtp_port = settings['smtp_port']
                config.smtp_use_tls = settings['smtp_use_tls']
                config.smtp_use_ssl = settings['smtp_use_ssl']
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid provider type'}), 400

    updateable_fields = [
        'is_enabled', 'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password',
        'smtp_use_tls', 'smtp_use_ssl', 'sender_email', 'sender_name', 'reply_to_email'
    ]
    for field in updateable_fields:
        if field in data:
            setattr(config, field, data[field])

    db.session.commit()

    return jsonify({
        'success': True,
        'config': config.to_dict(),
        'message': 'Email configuration updated successfully'
    })


@company_bp.route('/<company_id>/email-config/test', methods=['POST'])
@jwt_required()
def test_company_email_config(company_id):
    """Test company SMTP email configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyEmailConfig.query.filter_by(company_id=company_id).first()
    if not config:
        return jsonify({'success': False, 'error': 'Email configuration not found'}), 404

    from app.modules.notifications.smtp_client import SMTPClient
    from datetime import datetime

    client = SMTPClient(config)
    result = client.test_connection()

    # Update test status
    config.last_test_at = datetime.utcnow()
    config.last_test_success = result['success']
    config.last_error = result.get('error') if not result['success'] else None
    db.session.commit()

    return jsonify({
        'success': result['success'],
        'message': result.get('message', result.get('error', 'Test completed'))
    })


@company_bp.route('/<company_id>/email-config/send-test', methods=['POST'])
@jwt_required()
def send_test_email(company_id):
    """Send a test email using company SMTP configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    data = request.get_json()
    test_email = data.get('email', user.email)

    if not test_email:
        return jsonify({'success': False, 'error': 'Email address required'}), 400

    config = CompanyEmailConfig.query.filter_by(company_id=company_id).first()
    if not config or not config.is_enabled:
        return jsonify({'success': False, 'error': 'Email configuration not enabled'}), 400

    from app.modules.notifications.smtp_client import SMTPClient
    from datetime import datetime

    client = SMTPClient(config)
    result = client.send_email(
        to_email=test_email,
        subject='Test Email - Accountant CRM',
        body='''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563eb;">SMTP Configuration Test</h2>
            <p>This is a test email from your Accountant CRM system.</p>
            <p>If you received this email, your SMTP configuration is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Sent via company SMTP configuration</p>
        </body>
        </html>
        ''',
        is_html=True
    )

    # Update test status
    config.last_test_at = datetime.utcnow()
    config.last_test_success = result['success']
    config.last_error = result.get('error') if not result['success'] else None
    db.session.commit()

    if result['success']:
        return jsonify({
            'success': True,
            'message': f'Test email sent successfully to {test_email}'
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to send test email')
        }), 400


# ============== Company Storage Configuration Routes ==============

@company_bp.route('/<company_id>/storage-config', methods=['GET'])
@jwt_required()
def get_company_storage_config(company_id):
    """Get company document storage configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()

    return jsonify({
        'success': True,
        'config': config.to_dict() if config else None,
        'provider_options': [{'value': p.value, 'label': p.value.replace('_', ' ').title()} for p in StorageProviderType]
    })


@company_bp.route('/<company_id>/storage-config', methods=['PUT'])
@jwt_required()
def update_company_storage_config(company_id):
    """Update company document storage configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Only admins can update storage configuration'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    data = request.get_json()

    # Get or create config
    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if not config:
        import uuid
        config = CompanyStorageConfig(id=str(uuid.uuid4()), company_id=company_id)
        db.session.add(config)

    # Update fields
    if 'provider' in data:
        try:
            config.provider = StorageProviderType(data['provider'])
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid provider type'}), 400

    updateable_fields = [
        'is_enabled', 'sharepoint_site_id', 'sharepoint_drive_id', 'sharepoint_root_folder',
        'zoho_client_id', 'zoho_client_secret', 'zoho_root_folder_id', 'zoho_org_id',
        'google_client_id', 'google_client_secret', 'google_root_folder_id',
        'azure_connection_string', 'azure_container_name'
    ]
    for field in updateable_fields:
        if field in data:
            setattr(config, field, data[field])

    db.session.commit()

    return jsonify({
        'success': True,
        'config': config.to_dict(),
        'message': 'Storage configuration updated successfully'
    })


@company_bp.route('/<company_id>/storage-config/test', methods=['POST'])
@jwt_required()
def test_company_storage_config(company_id):
    """Test company storage configuration"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if not config:
        return jsonify({'success': False, 'error': 'Storage configuration not found'}), 404

    from datetime import datetime

    if config.provider == StorageProviderType.ZOHO_DRIVE:
        from app.modules.documents.zoho_drive_client import ZohoDriveClient
        client = ZohoDriveClient(config)
        result = client.test_connection()
    elif config.provider == StorageProviderType.SHAREPOINT:
        from app.modules.documents.sharepoint_client import SharePointClient
        # Use company-specific SharePoint config
        client = SharePointClient()
        result = client.test_connection() if hasattr(client, 'test_connection') else {'success': True}
    else:
        result = {'success': True, 'message': 'Local/Azure storage does not require connection test'}

    # Update status
    config.last_error = result.get('error') if not result.get('success', True) else None
    db.session.commit()

    return jsonify({
        'success': result.get('success', True),
        'message': result.get('message', result.get('error', 'Test completed'))
    })


# ============== Zoho Drive OAuth Routes ==============

@company_bp.route('/<company_id>/storage-config/zoho/auth-url', methods=['GET'])
@jwt_required()
def get_zoho_auth_url(company_id):
    """Get Zoho OAuth authorization URL"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if not config or not config.zoho_client_id:
        return jsonify({'success': False, 'error': 'Zoho client ID not configured'}), 400

    from flask import current_app
    from app.modules.documents.zoho_drive_client import ZohoDriveClient

    redirect_uri = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/settings/integrations/zoho/callback"
    auth_url = ZohoDriveClient.get_authorization_url(
        client_id=config.zoho_client_id,
        redirect_uri=redirect_uri,
        state=company_id
    )

    return jsonify({
        'success': True,
        'auth_url': auth_url
    })


@company_bp.route('/<company_id>/storage-config/zoho/callback', methods=['POST'])
@jwt_required()
def zoho_oauth_callback(company_id):
    """Handle Zoho OAuth callback - exchange code for tokens"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    data = request.get_json()
    code = data.get('code')

    if not code:
        return jsonify({'success': False, 'error': 'Authorization code required'}), 400

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if not config or not config.zoho_client_id or not config.zoho_client_secret:
        return jsonify({'success': False, 'error': 'Zoho credentials not configured'}), 400

    from flask import current_app
    from app.modules.documents.zoho_drive_client import ZohoDriveClient

    redirect_uri = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/settings/integrations/zoho/callback"

    result = ZohoDriveClient.exchange_code_for_tokens(
        client_id=config.zoho_client_id,
        client_secret=config.zoho_client_secret,
        code=code,
        redirect_uri=redirect_uri
    )

    if result['success']:
        config.zoho_access_token = result['access_token']
        config.zoho_refresh_token = result['refresh_token']
        config.zoho_token_expires_at = result['expires_at']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Zoho Drive connected successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to connect to Zoho Drive')
        }), 400


# ============== Google Drive OAuth Routes ==============

@company_bp.route('/<company_id>/storage-config/google/auth-url', methods=['GET'])
@jwt_required()
def get_google_auth_url(company_id):
    """Get Google Drive OAuth authorization URL"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if not config or not config.google_client_id:
        return jsonify({'success': False, 'error': 'Google client ID not configured'}), 400

    from flask import current_app
    from app.modules.documents.google_drive_client import GoogleDriveClient

    redirect_uri = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/settings/integrations/google/callback"
    auth_url = GoogleDriveClient.get_authorization_url(
        client_id=config.google_client_id,
        redirect_uri=redirect_uri,
        state=company_id
    )

    return jsonify({
        'success': True,
        'auth_url': auth_url
    })


@company_bp.route('/<company_id>/storage-config/google/callback', methods=['POST'])
@jwt_required()
def google_oauth_callback(company_id):
    """Handle Google OAuth callback - exchange code for tokens"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    data = request.get_json()
    code = data.get('code')

    if not code:
        return jsonify({'success': False, 'error': 'Authorization code required'}), 400

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if not config or not config.google_client_id or not config.google_client_secret:
        return jsonify({'success': False, 'error': 'Google credentials not configured'}), 400

    from flask import current_app
    from app.modules.documents.google_drive_client import GoogleDriveClient

    redirect_uri = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/settings/integrations/google/callback"

    try:
        result = GoogleDriveClient.exchange_code_for_tokens(
            client_id=config.google_client_id,
            client_secret=config.google_client_secret,
            code=code,
            redirect_uri=redirect_uri
        )

        config.google_access_token = result['access_token']
        config.google_refresh_token = result.get('refresh_token')
        config.google_token_expires_at = result['expires_at']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Google Drive connected successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@company_bp.route('/<company_id>/storage-config/google/disconnect', methods=['POST'])
@jwt_required()
def disconnect_google_drive(company_id):
    """Disconnect Google Drive - remove tokens"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check permission
    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    config = CompanyStorageConfig.query.filter_by(company_id=company_id).first()
    if config:
        config.google_access_token = None
        config.google_refresh_token = None
        config.google_token_expires_at = None
        db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Google Drive disconnected successfully'
    })


# ============== System Email Configuration Routes (Super Admin) ==============

@company_bp.route('/system/email-config', methods=['GET'])
@jwt_required()
def get_system_email_config():
    """Get system-level SMTP email configuration (Super Admin only)"""
    user_id = get_jwt_identity()
    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    config = SystemEmailConfig.get_config()

    return jsonify({
        'success': True,
        'config': config.to_dict() if config else None,
        'provider_options': [{'value': p.value, 'label': p.value.title()} for p in EmailProviderType],
        'provider_settings': CompanyEmailConfig.PROVIDER_SETTINGS
    })


@company_bp.route('/system/email-config', methods=['PUT'])
@jwt_required()
def update_system_email_config():
    """Update system-level SMTP email configuration (Super Admin only)"""
    user_id = get_jwt_identity()
    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    data = request.get_json()
    config = SystemEmailConfig.get_config()

    # Update fields
    if 'provider' in data:
        try:
            config.provider = EmailProviderType(data['provider'])
            # Auto-fill provider settings
            if config.provider.value in CompanyEmailConfig.PROVIDER_SETTINGS:
                settings = CompanyEmailConfig.PROVIDER_SETTINGS[config.provider.value]
                config.smtp_host = settings['smtp_host']
                config.smtp_port = settings['smtp_port']
                config.smtp_use_tls = settings['smtp_use_tls']
                config.smtp_use_ssl = settings['smtp_use_ssl']
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid provider type'}), 400

    updateable_fields = [
        'is_enabled', 'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password',
        'smtp_use_tls', 'smtp_use_ssl', 'sender_email', 'sender_name', 'use_as_fallback'
    ]
    for field in updateable_fields:
        if field in data:
            setattr(config, field, data[field])

    db.session.commit()

    return jsonify({
        'success': True,
        'config': config.to_dict(),
        'message': 'System email configuration updated successfully'
    })


@company_bp.route('/system/email-config/test', methods=['POST'])
@jwt_required()
def test_system_email_config():
    """Test system-level SMTP configuration (Super Admin only)"""
    user_id = get_jwt_identity()
    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    config = SystemEmailConfig.get_config()

    from app.modules.notifications.smtp_client import SMTPClient
    from datetime import datetime

    client = SMTPClient(config)
    result = client.test_connection()

    # Update test status
    config.last_test_at = datetime.utcnow()
    config.last_test_success = result['success']
    config.last_error = result.get('error') if not result['success'] else None
    db.session.commit()

    return jsonify({
        'success': result['success'],
        'message': result.get('message', result.get('error', 'Test completed'))
    })


@company_bp.route('/system/email-config/send-test', methods=['POST'])
@jwt_required()
def send_system_test_email():
    """Send a test email using system SMTP configuration (Super Admin only)"""
    user_id = get_jwt_identity()
    is_admin, error_response, status = _check_super_admin(user_id)
    if not is_admin:
        return error_response, status

    user = User.query.get(user_id)
    data = request.get_json()
    test_email = data.get('email', user.email)

    if not test_email:
        return jsonify({'success': False, 'error': 'Email address required'}), 400

    config = SystemEmailConfig.get_config()
    if not config or not config.is_enabled:
        return jsonify({'success': False, 'error': 'System email configuration not enabled'}), 400

    from app.modules.notifications.smtp_client import SMTPClient
    from datetime import datetime

    client = SMTPClient(config)
    result = client.send_email(
        to_email=test_email,
        subject='System Test Email - Accountant CRM',
        body='''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563eb;">System SMTP Configuration Test</h2>
            <p>This is a test email from your Accountant CRM system.</p>
            <p>If you received this email, your system SMTP configuration is working correctly!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Sent via system SMTP configuration (Super Admin)</p>
        </body>
        </html>
        ''',
        is_html=True
    )

    # Update test status
    config.last_test_at = datetime.utcnow()
    config.last_test_success = result['success']
    config.last_error = result.get('error') if not result['success'] else None
    db.session.commit()

    if result['success']:
        return jsonify({
            'success': True,
            'message': f'Test email sent successfully to {test_email}'
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to send test email')
        }), 400
