"""
Connect to Xero Use Case

Handles the OAuth flow and connection establishment with Xero.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConnectXeroUseCase:
    """
    Use case for connecting to Xero via OAuth.

    Steps:
    1. Generate authorization URL
    2. Handle OAuth callback
    3. Store connection details
    """

    def __init__(self, repository, auth_client):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            auth_client: XeroAuthClient instance
        """
        self.repository = repository
        self.auth_client = auth_client

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Xero authorization URL.

        Args:
            state: CSRF protection state string

        Returns:
            Authorization URL
        """
        return self.auth_client.get_authorization_url(state)

    def handle_callback(
        self,
        code: str,
        company_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback from Xero.

        Args:
            code: Authorization code from Xero
            company_id: CRM company ID
            user_id: User ID who initiated connection

        Returns:
            Result dict with connection details or error
        """
        try:
            # Exchange code for tokens
            token_data = self.auth_client.exchange_code_for_tokens(code)

            if not token_data:
                return {
                    'success': False,
                    'error': 'Failed to exchange authorization code for tokens'
                }

            # Get connected tenants
            connections = self.auth_client.get_connections(token_data['access_token'])

            if not connections or len(connections) == 0:
                return {
                    'success': False,
                    'error': 'No Xero organizations found'
                }

            # Use the first tenant
            tenant = connections[0]

            # Check for existing connection
            existing = self.repository.get_connection_by_company(company_id)

            if existing:
                # Update existing connection
                self.repository.update_connection(
                    existing,
                    xero_tenant_id=tenant['tenantId'],
                    xero_tenant_name=tenant.get('tenantName'),
                    xero_tenant_type=tenant.get('tenantType'),
                    is_active=True,
                    last_error=None,
                    disconnected_at=None
                )
                existing.update_tokens(
                    access_token=token_data['access_token'],
                    refresh_token=token_data['refresh_token'],
                    expires_in=token_data['expires_in'],
                    scopes=token_data.get('scope')
                )
                connection = existing
            else:
                # Create new connection
                connection = self.repository.create_connection(
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

            self.repository.commit()
            logger.info(f"Xero connected successfully for company {company_id}")

            return {
                'success': True,
                'connection': connection.to_dict(),
                'tenant_name': tenant.get('tenantName')
            }

        except Exception as e:
            logger.error(f"Error connecting to Xero: {str(e)}")
            self.repository.rollback()
            return {
                'success': False,
                'error': str(e)
            }


class DisconnectXeroUseCase:
    """
    Use case for disconnecting from Xero.
    """

    def __init__(self, repository, auth_client):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            auth_client: XeroAuthClient instance
        """
        self.repository = repository
        self.auth_client = auth_client

    def execute(self, company_id: str) -> Dict[str, Any]:
        """
        Disconnect from Xero.

        Args:
            company_id: CRM company ID

        Returns:
            Result dict
        """
        try:
            connection = self.repository.get_active_connection_by_company(company_id)

            if not connection:
                return {
                    'success': False,
                    'error': 'No active Xero connection found'
                }

            # Revoke token at Xero
            self.auth_client.revoke_token(connection.refresh_token)

            # Mark as disconnected
            self.repository.disconnect(connection)
            self.repository.commit()

            logger.info(f"Xero disconnected for company {company_id}")

            return {
                'success': True,
                'message': 'Disconnected from Xero successfully'
            }

        except Exception as e:
            logger.error(f"Error disconnecting from Xero: {str(e)}")
            self.repository.rollback()
            return {
                'success': False,
                'error': str(e)
            }


class GetXeroStatusUseCase:
    """
    Use case for getting Xero connection status.
    """

    def __init__(self, repository):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
        """
        self.repository = repository

    def execute(self, company_id: str) -> Dict[str, Any]:
        """
        Get Xero connection status.

        Args:
            company_id: CRM company ID

        Returns:
            Status dict
        """
        connection = self.repository.get_connection_by_company(company_id)

        if not connection:
            return {
                'connected': False,
                'message': 'Not connected to Xero'
            }

        last_sync = self.repository.get_last_sync_log(connection.id)

        return {
            'connected': connection.is_active,
            'connection': connection.to_dict(),
            'last_sync': last_sync.to_dict() if last_sync else None
        }
