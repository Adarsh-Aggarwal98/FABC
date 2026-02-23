"""
Xero Integration API Routes

Standalone routes for Xero integration.
To enable, register the blueprint in your app:

    from app.modules.integrations.xero.routes import xero_bp
    app.register_blueprint(xero_bp, url_prefix='/api/integrations/xero')

Endpoints:
    GET  /connect          - Get Xero authorization URL
    GET  /callback         - OAuth callback handler
    POST /disconnect       - Disconnect from Xero
    GET  /status           - Get connection status
    POST /sync/contacts    - Sync contacts to Xero
    POST /sync/invoices    - Sync invoices to Xero
    POST /sync/all         - Full sync
    GET  /sync/logs        - Get sync history
    POST /push/invoice/:id - Push single invoice
    POST /push/contact/:id - Push single contact
    GET  /accounts         - Get Xero accounts (for mapping)
    GET  /organisation     - Get connected organisation info
"""

import os
import secrets
import logging
from functools import wraps
from flask import Blueprint, request, redirect, session, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

logger = logging.getLogger(__name__)

# Create blueprint
xero_bp = Blueprint('xero', __name__)


def get_xero_models():
    """
    Lazy load Xero models to avoid import issues.
    Returns tuple of model classes.
    """
    from app.extensions import db
    from app.modules.integrations.xero.models import create_xero_models
    return create_xero_models(db)


def get_crm_models():
    """Get CRM models for sync operations"""
    from app.modules.user.models import User
    from app.modules.company.models import Company
    try:
        from app.modules.services.models import Invoice
    except ImportError:
        Invoice = None
    return {'User': User, 'Company': Company, 'Invoice': Invoice}


def xero_configured(f):
    """Decorator to check if Xero is configured"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.modules.integrations.xero.xero_client import XeroConfig
        if not XeroConfig.is_configured():
            return {
                'success': False,
                'error': 'Xero integration not configured. Set XERO_CLIENT_ID and XERO_CLIENT_SECRET.'
            }, 501
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Get current user from JWT"""
    from app.modules.user.models import User
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def success_response(data, message=None, status_code=200):
    """Standard success response"""
    response = {'success': True, 'data': data}
    if message:
        response['message'] = message
    return response, status_code


def error_response(error, status_code=400):
    """Standard error response"""
    return {'success': False, 'error': error}, status_code


# ============== OAuth Routes ==============

@xero_bp.route('/connect', methods=['GET'])
@jwt_required()
@xero_configured
def get_connect_url():
    """
    Get the Xero authorization URL.
    Frontend should redirect user to this URL.
    """
    from app.modules.integrations.xero.xero_client import XeroAuthClient

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Only admins can connect to Xero', 403)

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session (or use JWT)
    session['xero_oauth_state'] = state
    session['xero_oauth_company_id'] = current_user.company_id
    session['xero_oauth_user_id'] = current_user.id

    auth_client = XeroAuthClient()
    auth_url = auth_client.get_authorization_url(state)

    return success_response({
        'authorization_url': auth_url,
        'state': state
    })


@xero_bp.route('/callback', methods=['GET'])
def oauth_callback():
    """
    Handle OAuth callback from Xero.
    This endpoint doesn't require JWT as it's called by Xero redirect.
    """
    from app.extensions import db
    from app.modules.integrations.xero.xero_client import XeroAuthClient

    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    # Get frontend URL for redirect
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

    if error:
        logger.error(f"Xero OAuth error: {error}")
        return redirect(f"{frontend_url}/settings/integrations?error={error}")

    # Verify state (CSRF protection)
    stored_state = session.get('xero_oauth_state')
    if not state or state != stored_state:
        logger.error("Invalid OAuth state")
        return redirect(f"{frontend_url}/settings/integrations?error=invalid_state")

    company_id = session.get('xero_oauth_company_id')
    user_id = session.get('xero_oauth_user_id')

    if not company_id:
        return redirect(f"{frontend_url}/settings/integrations?error=no_company")

    # Exchange code for tokens
    auth_client = XeroAuthClient()
    token_data = auth_client.exchange_code_for_tokens(code)

    if not token_data:
        return redirect(f"{frontend_url}/settings/integrations?error=token_exchange_failed")

    # Get connected tenants
    connections = auth_client.get_connections(token_data['access_token'])

    if not connections or len(connections) == 0:
        return redirect(f"{frontend_url}/settings/integrations?error=no_tenants")

    # Use the first tenant (or let user choose in future)
    tenant = connections[0]

    # Create or update connection
    XeroConnection, _, _, _ = get_xero_models()

    existing = XeroConnection.query.filter_by(company_id=company_id).first()

    if existing:
        # Update existing connection
        existing.xero_tenant_id = tenant['tenantId']
        existing.xero_tenant_name = tenant.get('tenantName')
        existing.xero_tenant_type = tenant.get('tenantType')
        existing.update_tokens(
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            expires_in=token_data['expires_in'],
            scopes=token_data.get('scope')
        )
        existing.is_active = True
        existing.last_error = None
        existing.disconnected_at = None
    else:
        # Create new connection
        connection = XeroConnection(
            company_id=company_id,
            xero_tenant_id=tenant['tenantId'],
            xero_tenant_name=tenant.get('tenantName'),
            xero_tenant_type=tenant.get('tenantType'),
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_expires_at=None,  # Will be set by update_tokens
            scopes=token_data.get('scope'),
            connected_by_id=user_id
        )
        connection.update_tokens(
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            expires_in=token_data['expires_in']
        )
        db.session.add(connection)

    db.session.commit()

    # Clear session data
    session.pop('xero_oauth_state', None)
    session.pop('xero_oauth_company_id', None)
    session.pop('xero_oauth_user_id', None)

    logger.info(f"Xero connected successfully for company {company_id}")
    return redirect(f"{frontend_url}/settings/integrations?xero=connected")


@xero_bp.route('/disconnect', methods=['POST'])
@jwt_required()
@xero_configured
def disconnect():
    """Disconnect from Xero"""
    from app.extensions import db
    from app.modules.integrations.xero.xero_client import XeroAuthClient
    from datetime import datetime

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Only admins can disconnect from Xero', 403)

    XeroConnection, _, _, _ = get_xero_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    # Revoke token at Xero
    auth_client = XeroAuthClient()
    auth_client.revoke_token(connection.refresh_token)

    # Mark as disconnected
    connection.is_active = False
    connection.disconnected_at = datetime.utcnow()
    db.session.commit()

    return success_response({'disconnected': True}, message='Xero disconnected successfully')


@xero_bp.route('/status', methods=['GET'])
@jwt_required()
@xero_configured
def get_status():
    """Get Xero connection status"""
    current_user = get_current_user()

    XeroConnection, _, _, XeroSyncLog = get_xero_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id
    ).first()

    if not connection:
        return success_response({
            'connected': False,
            'message': 'Not connected to Xero'
        })

    # Get last sync log
    last_sync = XeroSyncLog.query.filter_by(
        xero_connection_id=connection.id
    ).order_by(XeroSyncLog.started_at.desc()).first()

    return success_response({
        'connected': connection.is_active,
        'connection': connection.to_dict(),
        'last_sync': last_sync.to_dict() if last_sync else None
    })


# ============== Sync Routes ==============

@xero_bp.route('/sync/contacts', methods=['POST'])
@jwt_required()
@xero_configured
def sync_contacts():
    """Sync contacts to Xero"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Only admins can sync data', 403)

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)
    result = sync_service.sync_contacts(user_id=current_user.id, is_manual=True)

    if result['success']:
        return success_response(result, message='Contacts synced successfully')
    else:
        return error_response(result.get('error', 'Sync failed'))


@xero_bp.route('/sync/invoices', methods=['POST'])
@jwt_required()
@xero_configured
def sync_invoices():
    """Sync invoices to Xero"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Only admins can sync data', 403)

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)
    result = sync_service.sync_invoices(user_id=current_user.id, is_manual=True)

    if result['success']:
        return success_response(result, message='Invoices synced successfully')
    else:
        return error_response(result.get('error', 'Sync failed'))


@xero_bp.route('/sync/all', methods=['POST'])
@jwt_required()
@xero_configured
def sync_all():
    """Full sync - contacts and invoices"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Only admins can sync data', 403)

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)

    results = {
        'contacts': sync_service.sync_contacts(user_id=current_user.id, is_manual=True),
        'invoices': sync_service.sync_invoices(user_id=current_user.id, is_manual=True)
    }

    return success_response(results, message='Full sync completed')


@xero_bp.route('/sync/logs', methods=['GET'])
@jwt_required()
@xero_configured
def get_sync_logs():
    """Get sync history"""
    current_user = get_current_user()

    XeroConnection, _, _, XeroSyncLog = get_xero_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id
    ).first()

    if not connection:
        return success_response({'logs': []})

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    logs = XeroSyncLog.query.filter_by(
        xero_connection_id=connection.id
    ).order_by(
        XeroSyncLog.started_at.desc()
    ).paginate(page=page, per_page=per_page)

    return success_response({
        'logs': [log.to_dict() for log in logs.items],
        'pagination': {
            'page': logs.page,
            'per_page': logs.per_page,
            'total': logs.total,
            'pages': logs.pages
        }
    })


# ============== Push Single Item Routes ==============

@xero_bp.route('/push/invoice/<invoice_id>', methods=['POST'])
@jwt_required()
@xero_configured
def push_invoice(invoice_id):
    """Push a single invoice to Xero"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin', 'accountant']:
        return error_response('Insufficient permissions', 403)

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)
    result = sync_service.push_single_invoice_to_xero(invoice_id)

    if result and 'error' not in result:
        return success_response(result, message='Invoice pushed to Xero')
    else:
        return error_response(result.get('error', 'Failed to push invoice'))


@xero_bp.route('/push/contact/<user_id>', methods=['POST'])
@jwt_required()
@xero_configured
def push_contact(user_id):
    """Push a single contact to Xero"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin', 'accountant']:
        return error_response('Insufficient permissions', 403)

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)
    result = sync_service.push_single_contact_to_xero(user_id)

    if result:
        return success_response(result, message='Contact pushed to Xero')
    else:
        return error_response('Failed to push contact')


# ============== Utility Routes ==============

@xero_bp.route('/accounts', methods=['GET'])
@jwt_required()
@xero_configured
def get_accounts():
    """Get Xero accounts for mapping configuration"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)

    account_type = request.args.get('type')  # BANK, REVENUE, etc.

    if account_type:
        result = sync_service.api_client.get_accounts(account_type)
    else:
        result = sync_service.get_xero_accounts()

    if result:
        return success_response(result)
    else:
        return error_response('Failed to retrieve accounts')


@xero_bp.route('/organisation', methods=['GET'])
@jwt_required()
@xero_configured
def get_organisation():
    """Get connected Xero organisation details"""
    from app.extensions import db
    from app.modules.integrations.xero.sync_service import XeroSyncService

    current_user = get_current_user()

    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = get_xero_models()
    crm_models = get_crm_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    models = {
        'XeroConnection': XeroConnection,
        'XeroContactMapping': XeroContactMapping,
        'XeroInvoiceMapping': XeroInvoiceMapping,
        'XeroSyncLog': XeroSyncLog,
        **crm_models
    }

    sync_service = XeroSyncService(db, connection, models)
    result = sync_service.test_connection()

    if result['success']:
        return success_response(result)
    else:
        return error_response(result.get('error', 'Failed to get organisation'))


@xero_bp.route('/settings', methods=['GET', 'PUT'])
@jwt_required()
@xero_configured
def connection_settings():
    """Get or update Xero connection settings"""
    from app.extensions import db

    current_user = get_current_user()
    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Only admins can manage Xero settings', 403)

    XeroConnection, _, _, _ = get_xero_models()

    connection = XeroConnection.query.filter_by(
        company_id=current_user.company_id,
        is_active=True
    ).first()

    if not connection:
        return error_response('No active Xero connection', 404)

    if request.method == 'GET':
        return success_response(connection.to_dict())

    # PUT - Update settings
    data = request.get_json()

    if 'auto_sync_contacts' in data:
        connection.auto_sync_contacts = data['auto_sync_contacts']
    if 'auto_sync_invoices' in data:
        connection.auto_sync_invoices = data['auto_sync_invoices']
    if 'sync_interval_minutes' in data:
        connection.sync_interval_minutes = data['sync_interval_minutes']
    if 'default_sales_account_id' in data:
        connection.default_sales_account_id = data['default_sales_account_id']
    if 'default_bank_account_id' in data:
        connection.default_bank_account_id = data['default_bank_account_id']

    db.session.commit()

    return success_response(connection.to_dict(), message='Settings updated')
