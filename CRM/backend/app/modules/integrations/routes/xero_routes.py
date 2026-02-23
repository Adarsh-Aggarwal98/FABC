"""
Xero Routes

Thin controllers for Xero integration API endpoints.
Business logic is delegated to use cases.
"""

import os
import secrets
import logging
from functools import wraps
from flask import Blueprint, request, redirect, session

logger = logging.getLogger(__name__)

# Create blueprint
xero_bp = Blueprint('xero', __name__)


def init_xero_routes(db, jwt_required, get_jwt_identity):
    """
    Initialize Xero routes with dependencies.

    Args:
        db: SQLAlchemy database instance
        jwt_required: JWT decorator
        get_jwt_identity: Function to get current user ID

    Returns:
        Configured blueprint
    """
    from ..models import create_xero_models
    from ..services import XeroConfig, XeroAuthClient, XeroAPIClient
    from ..repositories import XeroRepository
    from ..schemas import success_response, error_response

    # Create models
    XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog = create_xero_models(db)

    def get_xero_models():
        """Get Xero model classes"""
        return XeroConnection, XeroContactMapping, XeroInvoiceMapping, XeroSyncLog

    def get_repository():
        """Get repository instance with models"""
        models = {
            'XeroConnection': XeroConnection,
            'XeroContactMapping': XeroContactMapping,
            'XeroInvoiceMapping': XeroInvoiceMapping,
            'XeroSyncLog': XeroSyncLog
        }
        return XeroRepository(db, models)

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
            if not XeroConfig.is_configured():
                return error_response(
                    'Xero integration not configured. Set XERO_CLIENT_ID and XERO_CLIENT_SECRET.',
                    501
                )
            return f(*args, **kwargs)
        return decorated

    def get_current_user():
        """Get current user from JWT"""
        from app.modules.user.models import User
        user_id = get_jwt_identity()
        return User.query.get(user_id)

    # ============== OAuth Routes ==============

    @xero_bp.route('/connect', methods=['GET'])
    @jwt_required()
    @xero_configured
    def get_connect_url():
        """Get Xero authorization URL"""
        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin']:
            return error_response('Only admins can connect to Xero', 403)

        state = secrets.token_urlsafe(32)
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
        """Handle OAuth callback from Xero"""
        from ..usecases import ConnectXeroUseCase

        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

        if error:
            logger.error(f"Xero OAuth error: {error}")
            return redirect(f"{frontend_url}/settings/integrations?error={error}")

        stored_state = session.get('xero_oauth_state')
        if not state or state != stored_state:
            return redirect(f"{frontend_url}/settings/integrations?error=invalid_state")

        company_id = session.get('xero_oauth_company_id')
        user_id = session.get('xero_oauth_user_id')

        if not company_id:
            return redirect(f"{frontend_url}/settings/integrations?error=no_company")

        # Use case handles the connection logic
        repository = get_repository()
        auth_client = XeroAuthClient()
        use_case = ConnectXeroUseCase(repository, auth_client)

        result = use_case.handle_callback(code, company_id, user_id)

        # Clear session
        session.pop('xero_oauth_state', None)
        session.pop('xero_oauth_company_id', None)
        session.pop('xero_oauth_user_id', None)

        if result['success']:
            return redirect(f"{frontend_url}/settings/integrations?xero=connected")
        else:
            return redirect(f"{frontend_url}/settings/integrations?error={result.get('error', 'unknown')}")

    @xero_bp.route('/disconnect', methods=['POST'])
    @jwt_required()
    @xero_configured
    def disconnect():
        """Disconnect from Xero"""
        from ..usecases import DisconnectXeroUseCase

        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin']:
            return error_response('Only admins can disconnect from Xero', 403)

        repository = get_repository()
        auth_client = XeroAuthClient()
        use_case = DisconnectXeroUseCase(repository, auth_client)

        result = use_case.execute(current_user.company_id)

        if result['success']:
            return success_response({'disconnected': True}, result.get('message'))
        else:
            return error_response(result.get('error', 'Disconnect failed'))

    @xero_bp.route('/status', methods=['GET'])
    @jwt_required()
    @xero_configured
    def get_status():
        """Get Xero connection status"""
        from ..usecases import GetXeroStatusUseCase

        current_user = get_current_user()
        repository = get_repository()
        use_case = GetXeroStatusUseCase(repository)

        result = use_case.execute(current_user.company_id)
        return success_response(result)

    # ============== Sync Routes ==============

    @xero_bp.route('/sync/contacts', methods=['POST'])
    @jwt_required()
    @xero_configured
    def sync_contacts():
        """Sync contacts to Xero"""
        from ..usecases import SyncXeroContactsUseCase

        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin']:
            return error_response('Only admins can sync data', 403)

        repository = get_repository()
        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        # Refresh token if needed
        if connection.is_token_expired():
            auth_client = XeroAuthClient()
            token_data = auth_client.refresh_access_token(connection.refresh_token)
            if token_data:
                connection.update_tokens(
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token', connection.refresh_token),
                    expires_in=token_data['expires_in']
                )
                repository.commit()

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        crm_models = get_crm_models()

        use_case = SyncXeroContactsUseCase(repository, api_client, crm_models['User'])

        result = use_case.execute(
            connection_id=connection.id,
            company_id=current_user.company_id,
            user_id=current_user.id,
            is_manual=True
        )

        if result['success']:
            return success_response(result, 'Contacts synced successfully')
        else:
            return error_response(result.get('error', 'Sync failed'))

    @xero_bp.route('/sync/invoices', methods=['POST'])
    @jwt_required()
    @xero_configured
    def sync_invoices():
        """Sync invoices to Xero"""
        from ..usecases import SyncXeroInvoicesUseCase

        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin']:
            return error_response('Only admins can sync data', 403)

        repository = get_repository()
        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        # Refresh token if needed
        if connection.is_token_expired():
            auth_client = XeroAuthClient()
            token_data = auth_client.refresh_access_token(connection.refresh_token)
            if token_data:
                connection.update_tokens(
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token', connection.refresh_token),
                    expires_in=token_data['expires_in']
                )
                repository.commit()

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        crm_models = get_crm_models()

        use_case = SyncXeroInvoicesUseCase(
            repository, api_client, crm_models.get('Invoice'), connection
        )

        result = use_case.execute(
            company_id=current_user.company_id,
            user_id=current_user.id,
            is_manual=True
        )

        if result['success']:
            return success_response(result, 'Invoices synced successfully')
        else:
            return error_response(result.get('error', 'Sync failed'))

    @xero_bp.route('/sync/all', methods=['POST'])
    @jwt_required()
    @xero_configured
    def sync_all():
        """Full sync - contacts and invoices"""
        from ..usecases import SyncXeroContactsUseCase, SyncXeroInvoicesUseCase

        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin']:
            return error_response('Only admins can sync data', 403)

        repository = get_repository()
        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        # Refresh token if needed
        if connection.is_token_expired():
            auth_client = XeroAuthClient()
            token_data = auth_client.refresh_access_token(connection.refresh_token)
            if token_data:
                connection.update_tokens(
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token', connection.refresh_token),
                    expires_in=token_data['expires_in']
                )
                repository.commit()

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        crm_models = get_crm_models()

        # Sync contacts
        contacts_use_case = SyncXeroContactsUseCase(repository, api_client, crm_models['User'])
        contacts_result = contacts_use_case.execute(
            connection_id=connection.id,
            company_id=current_user.company_id,
            user_id=current_user.id,
            is_manual=True
        )

        # Sync invoices
        invoices_use_case = SyncXeroInvoicesUseCase(
            repository, api_client, crm_models.get('Invoice'), connection
        )
        invoices_result = invoices_use_case.execute(
            company_id=current_user.company_id,
            user_id=current_user.id,
            is_manual=True
        )

        return success_response({
            'contacts': contacts_result,
            'invoices': invoices_result
        }, 'Full sync completed')

    @xero_bp.route('/sync/logs', methods=['GET'])
    @jwt_required()
    @xero_configured
    def get_sync_logs():
        """Get sync history"""
        current_user = get_current_user()
        repository = get_repository()

        connection = repository.get_connection_by_company(current_user.company_id)

        if not connection:
            return success_response({'logs': []})

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        logs = repository.get_sync_logs(connection.id, page, per_page)

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
        from ..usecases import PushSingleInvoiceToXeroUseCase

        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin', 'accountant']:
            return error_response('Insufficient permissions', 403)

        repository = get_repository()
        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        crm_models = get_crm_models()

        use_case = PushSingleInvoiceToXeroUseCase(
            repository, api_client, crm_models.get('Invoice'), connection
        )

        result = use_case.execute(invoice_id)

        if result['success']:
            return success_response(result.get('data'), 'Invoice pushed to Xero')
        else:
            return error_response(result.get('error', 'Failed to push invoice'))

    @xero_bp.route('/push/contact/<user_id>', methods=['POST'])
    @jwt_required()
    @xero_configured
    def push_contact(user_id):
        """Push a single contact to Xero"""
        from ..usecases import PushSingleContactToXeroUseCase

        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin', 'accountant']:
            return error_response('Insufficient permissions', 403)

        repository = get_repository()
        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        crm_models = get_crm_models()

        use_case = PushSingleContactToXeroUseCase(repository, api_client, crm_models['User'])

        result = use_case.execute(connection.id, user_id)

        if result['success']:
            return success_response(result.get('data'), 'Contact pushed to Xero')
        else:
            return error_response(result.get('error', 'Failed to push contact'))

    # ============== Settings Routes ==============

    @xero_bp.route('/settings', methods=['GET', 'PUT'])
    @jwt_required()
    @xero_configured
    def connection_settings():
        """Get or update Xero connection settings"""
        current_user = get_current_user()
        if current_user.role.name not in ['super_admin', 'admin']:
            return error_response('Only admins can manage Xero settings', 403)

        repository = get_repository()
        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        if request.method == 'GET':
            return success_response(connection.to_dict())

        # PUT - Update settings
        data = request.get_json()
        update_fields = {}

        if 'auto_sync_contacts' in data:
            update_fields['auto_sync_contacts'] = data['auto_sync_contacts']
        if 'auto_sync_invoices' in data:
            update_fields['auto_sync_invoices'] = data['auto_sync_invoices']
        if 'sync_interval_minutes' in data:
            update_fields['sync_interval_minutes'] = data['sync_interval_minutes']
        if 'default_sales_account_id' in data:
            update_fields['default_sales_account_id'] = data['default_sales_account_id']
        if 'default_bank_account_id' in data:
            update_fields['default_bank_account_id'] = data['default_bank_account_id']

        repository.update_connection(connection, **update_fields)
        repository.commit()

        return success_response(connection.to_dict(), 'Settings updated')

    @xero_bp.route('/accounts', methods=['GET'])
    @jwt_required()
    @xero_configured
    def get_accounts():
        """Get Xero accounts for mapping"""
        current_user = get_current_user()
        repository = get_repository()

        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        account_type = request.args.get('type')

        result = api_client.get_accounts(account_type)

        if result:
            return success_response(result)
        else:
            return error_response('Failed to retrieve accounts')

    @xero_bp.route('/organisation', methods=['GET'])
    @jwt_required()
    @xero_configured
    def get_organisation():
        """Get connected Xero organisation details"""
        current_user = get_current_user()
        repository = get_repository()

        connection = repository.get_active_connection_by_company(current_user.company_id)

        if not connection:
            return error_response('No active Xero connection', 404)

        api_client = XeroAPIClient(connection.access_token, connection.xero_tenant_id)
        result = api_client.get_organisation()

        if result and 'Organisations' in result:
            org_data = result['Organisations'][0]
            return success_response({
                'success': True,
                'organisation': {
                    'name': org_data.get('Name'),
                    'legal_name': org_data.get('LegalName'),
                    'country': org_data.get('CountryCode'),
                    'base_currency': org_data.get('BaseCurrency'),
                    'organisation_type': org_data.get('OrganisationType')
                }
            })
        else:
            return error_response('Failed to get organisation')

    return xero_bp
