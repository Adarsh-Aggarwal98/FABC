"""
Xero Service

OAuth 2.0 client and API wrapper for Xero integration.
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class XeroConfig:
    """Xero configuration from environment variables"""

    CLIENT_ID = os.environ.get('XERO_CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('XERO_CLIENT_SECRET', '')
    REDIRECT_URI = os.environ.get('XERO_REDIRECT_URI', 'http://localhost:5001/api/integrations/xero/callback')

    # Xero OAuth endpoints
    AUTHORIZE_URL = 'https://login.xero.com/identity/connect/authorize'
    TOKEN_URL = 'https://identity.xero.com/connect/token'
    CONNECTIONS_URL = 'https://api.xero.com/connections'

    # Xero API base URL
    API_BASE_URL = 'https://api.xero.com/api.xro/2.0'

    # OAuth scopes needed for integration
    SCOPES = [
        'openid',
        'profile',
        'email',
        'accounting.contacts',
        'accounting.contacts.read',
        'accounting.transactions',
        'accounting.transactions.read',
        'accounting.settings.read',
        'offline_access'
    ]

    @classmethod
    def is_configured(cls) -> bool:
        """Check if Xero integration is properly configured"""
        return bool(cls.CLIENT_ID and cls.CLIENT_SECRET)


class XeroAuthClient:
    """
    Handles Xero OAuth 2.0 authentication flow.
    """

    def __init__(self):
        if not XeroConfig.is_configured():
            logger.warning("Xero integration not configured. Set XERO_CLIENT_ID and XERO_CLIENT_SECRET.")

    def get_authorization_url(self, state: str) -> str:
        """
        Generate the Xero authorization URL for OAuth flow.

        Args:
            state: Random state string for CSRF protection

        Returns:
            Authorization URL to redirect the user to
        """
        params = {
            'response_type': 'code',
            'client_id': XeroConfig.CLIENT_ID,
            'redirect_uri': XeroConfig.REDIRECT_URI,
            'scope': ' '.join(XeroConfig.SCOPES),
            'state': state
        }
        return f"{XeroConfig.AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from Xero callback

        Returns:
            Token response containing access_token, refresh_token, expires_in
        """
        try:
            response = requests.post(
                XeroConfig.TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': XeroConfig.REDIRECT_URI
                },
                auth=(XeroConfig.CLIENT_ID, XeroConfig.CLIENT_SECRET),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully exchanged code for Xero tokens")
                return token_data
            else:
                logger.error(f"Failed to exchange code: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh the access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token response
        """
        try:
            response = requests.post(
                XeroConfig.TOKEN_URL,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                },
                auth=(XeroConfig.CLIENT_ID, XeroConfig.CLIENT_SECRET),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully refreshed Xero access token")
                return token_data
            else:
                logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None

    def get_connections(self, access_token: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of Xero tenants (organizations) connected to the app.

        Args:
            access_token: Valid access token

        Returns:
            List of connected tenants
        """
        try:
            response = requests.get(
                XeroConfig.CONNECTIONS_URL,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get connections: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting connections: {str(e)}")
            return None

    def revoke_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token (disconnect from Xero).

        Args:
            refresh_token: Token to revoke

        Returns:
            True if successful
        """
        try:
            response = requests.post(
                'https://identity.xero.com/connect/revocation',
                data={
                    'token': refresh_token,
                    'token_type_hint': 'refresh_token'
                },
                auth=(XeroConfig.CLIENT_ID, XeroConfig.CLIENT_SECRET),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                logger.info("Successfully revoked Xero token")
                return True
            else:
                logger.error(f"Failed to revoke token: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            return False


class XeroAPIClient:
    """
    Xero API client for making authenticated API calls.
    """

    def __init__(self, access_token: str, tenant_id: str):
        """
        Initialize Xero API client.

        Args:
            access_token: Valid Xero access token
            tenant_id: Xero tenant ID (organization ID)
        """
        self.access_token = access_token
        self.tenant_id = tenant_id
        self.base_url = XeroConfig.API_BASE_URL

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Xero-tenant-id': self.tenant_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """
        Make an authenticated request to Xero API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/Contacts')
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON or None on error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                params=params
            )

            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                logger.error("Xero API: Unauthorized - token may be expired")
                return None
            elif response.status_code == 429:
                logger.warning("Xero API: Rate limited")
                return None
            else:
                logger.error(f"Xero API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Xero API request failed: {str(e)}")
            return None

    # ============== Contacts API ==============

    def get_contacts(self, page: int = 1, modified_after: datetime = None) -> Optional[Dict]:
        """Get contacts from Xero."""
        params = {'page': page}
        return self._make_request('GET', '/Contacts', params=params)

    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """Get a single contact by ID"""
        return self._make_request('GET', f'/Contacts/{contact_id}')

    def create_contact(self, contact_data: Dict) -> Optional[Dict]:
        """Create a new contact in Xero."""
        return self._make_request('POST', '/Contacts', data={'Contacts': [contact_data]})

    def update_contact(self, contact_id: str, contact_data: Dict) -> Optional[Dict]:
        """Update an existing contact"""
        contact_data['ContactID'] = contact_id
        return self._make_request('POST', '/Contacts', data={'Contacts': [contact_data]})

    def search_contacts(self, search_term: str) -> Optional[Dict]:
        """Search contacts by name or email"""
        params = {
            'where': f'Name.Contains("{search_term}") OR EmailAddress.Contains("{search_term}")'
        }
        return self._make_request('GET', '/Contacts', params=params)

    # ============== Invoices API ==============

    def get_invoices(self, page: int = 1, status: str = None, modified_after: datetime = None) -> Optional[Dict]:
        """Get invoices from Xero."""
        params = {'page': page}
        if status:
            params['Statuses'] = status
        return self._make_request('GET', '/Invoices', params=params)

    def get_invoice(self, invoice_id: str) -> Optional[Dict]:
        """Get a single invoice by ID"""
        return self._make_request('GET', f'/Invoices/{invoice_id}')

    def create_invoice(self, invoice_data: Dict) -> Optional[Dict]:
        """Create a new invoice in Xero."""
        return self._make_request('POST', '/Invoices', data={'Invoices': [invoice_data]})

    def update_invoice(self, invoice_id: str, invoice_data: Dict) -> Optional[Dict]:
        """Update an existing invoice"""
        invoice_data['InvoiceID'] = invoice_id
        return self._make_request('POST', '/Invoices', data={'Invoices': [invoice_data]})

    def void_invoice(self, invoice_id: str) -> Optional[Dict]:
        """Void an invoice"""
        return self._make_request('POST', '/Invoices', data={
            'Invoices': [{'InvoiceID': invoice_id, 'Status': 'VOIDED'}]
        })

    def get_invoice_as_pdf(self, invoice_id: str) -> Optional[bytes]:
        """Get invoice as PDF"""
        url = f"{self.base_url}/Invoices/{invoice_id}"
        try:
            response = requests.get(
                url,
                headers={
                    **self._get_headers(),
                    'Accept': 'application/pdf'
                }
            )
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            logger.error(f"Error getting invoice PDF: {str(e)}")
            return None

    # ============== Payments API ==============

    def get_payments(self, invoice_id: str = None) -> Optional[Dict]:
        """Get payments, optionally filtered by invoice"""
        params = {}
        if invoice_id:
            params['where'] = f'Invoice.InvoiceID==Guid("{invoice_id}")'
        return self._make_request('GET', '/Payments', params=params)

    def create_payment(self, payment_data: Dict) -> Optional[Dict]:
        """Record a payment against an invoice."""
        return self._make_request('PUT', '/Payments', data={'Payments': [payment_data]})

    # ============== Accounts API ==============

    def get_accounts(self, account_type: str = None) -> Optional[Dict]:
        """Get chart of accounts."""
        params = {}
        if account_type:
            params['where'] = f'Type=="{account_type}"'
        return self._make_request('GET', '/Accounts', params=params)

    def get_bank_accounts(self) -> Optional[Dict]:
        """Get bank accounts only"""
        return self.get_accounts(account_type='BANK')

    # ============== Organisation API ==============

    def get_organisation(self) -> Optional[Dict]:
        """Get organisation (tenant) details"""
        return self._make_request('GET', '/Organisation')

    # ============== Tax Rates API ==============

    def get_tax_rates(self) -> Optional[Dict]:
        """Get tax rates"""
        return self._make_request('GET', '/TaxRates')

    # ============== Items API ==============

    def get_items(self) -> Optional[Dict]:
        """Get inventory items"""
        return self._make_request('GET', '/Items')

    def create_item(self, item_data: Dict) -> Optional[Dict]:
        """Create an inventory item"""
        return self._make_request('POST', '/Items', data={'Items': [item_data]})
