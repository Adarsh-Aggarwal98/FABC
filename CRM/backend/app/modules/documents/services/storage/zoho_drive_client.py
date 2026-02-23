"""
Zoho Drive Client for document storage
Supports OAuth 2.0 authentication and file operations
"""
import os
import uuid
import requests
from datetime import datetime, timedelta
from flask import current_app


class ZohoDriveClient:
    """Client for interacting with Zoho WorkDrive API"""

    BASE_URL = 'https://workdrive.zoho.com/api/v1'
    AUTH_URL = 'https://accounts.zoho.com/oauth/v2'

    def __init__(self, config=None):
        """
        Initialize Zoho Drive client with configuration.

        Args:
            config: CompanyStorageConfig object or dict with Zoho settings
        """
        self.config = config
        self._extract_settings()

    def _extract_settings(self):
        """Extract Zoho settings from config"""
        if self.config is None:
            self.client_id = None
            self.client_secret = None
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            self.root_folder_id = None
            self.org_id = None
            return

        if hasattr(self.config, 'zoho_client_id'):
            # It's a model object
            self.client_id = self.config.zoho_client_id
            self.client_secret = self.config.zoho_client_secret
            self.access_token = self.config.zoho_access_token
            self.refresh_token = self.config.zoho_refresh_token
            self.token_expires_at = self.config.zoho_token_expires_at
            self.root_folder_id = self.config.zoho_root_folder_id
            self.org_id = self.config.zoho_org_id
        else:
            # It's a dict
            self.client_id = self.config.get('zoho_client_id')
            self.client_secret = self.config.get('zoho_client_secret')
            self.access_token = self.config.get('zoho_access_token')
            self.refresh_token = self.config.get('zoho_refresh_token')
            self.token_expires_at = self.config.get('zoho_token_expires_at')
            self.root_folder_id = self.config.get('zoho_root_folder_id')
            self.org_id = self.config.get('zoho_org_id')

    def is_configured(self):
        """Check if Zoho Drive is properly configured"""
        return all([
            self.client_id,
            self.client_secret,
            self.refresh_token,
            self.root_folder_id
        ])

    def _ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if needed"""
        if not self.refresh_token:
            raise ValueError('Zoho refresh token not available')

        # Check if token is expired or will expire in next 5 minutes
        if self.token_expires_at:
            if isinstance(self.token_expires_at, str):
                self.token_expires_at = datetime.fromisoformat(self.token_expires_at)
            if self.token_expires_at > datetime.utcnow() + timedelta(minutes=5):
                return  # Token is still valid

        # Refresh the token
        self._refresh_access_token()

    def _refresh_access_token(self):
        """Refresh the access token using refresh token"""
        try:
            response = requests.post(
                f'{self.AUTH_URL}/token',
                data={
                    'grant_type': 'refresh_token',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': self.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                expires_in = data.get('expires_in', 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                # Update config if it's a model object
                if hasattr(self.config, 'zoho_access_token'):
                    from app.extensions import db
                    self.config.zoho_access_token = self.access_token
                    self.config.zoho_token_expires_at = self.token_expires_at
                    db.session.commit()
            else:
                raise Exception(f'Failed to refresh token: {response.text}')

        except Exception as e:
            current_app.logger.error(f'Zoho token refresh failed: {str(e)}')
            raise

    def _get_headers(self):
        """Get headers for API requests"""
        self._ensure_valid_token()
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _sanitize_folder_name(self, name):
        """Sanitize folder/file name for Zoho"""
        # Remove or replace invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()[:255]  # Zoho has 255 char limit

    def _get_or_create_folder(self, parent_id, folder_name):
        """Get existing folder or create new one"""
        try:
            folder_name = self._sanitize_folder_name(folder_name)

            # Search for existing folder
            headers = self._get_headers()
            search_url = f'{self.BASE_URL}/files/{parent_id}/files'
            params = {'filter': f'name:{folder_name}', 'type': 'folder'}

            response = requests.get(search_url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                files = data.get('data', [])
                for file in files:
                    if file.get('attributes', {}).get('name') == folder_name:
                        return file.get('id')

            # Create new folder
            create_url = f'{self.BASE_URL}/files/{parent_id}/files'
            payload = {
                'data': {
                    'attributes': {
                        'name': folder_name,
                        'parent_id': parent_id
                    },
                    'type': 'files'
                }
            }

            response = requests.post(create_url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                data = response.json()
                return data.get('data', {}).get('id')
            else:
                current_app.logger.error(f'Failed to create Zoho folder: {response.text}')
                return None

        except Exception as e:
            current_app.logger.error(f'Error getting/creating Zoho folder: {str(e)}')
            return None

    def upload_file(self, file_stream, original_filename, client_name=None,
                    category='supporting_document', service_request_id=None,
                    company_name=None, username=None, service_name=None):
        """
        Upload a file to Zoho Drive with organized folder structure.

        Folder structure: root/{company_name}/{username}/{service_name}/{filename}
        Falls back to legacy structure if new parameters not provided.

        Args:
            file_stream: File stream to upload
            original_filename: Original filename
            client_name: Client name for folder organization (legacy)
            category: Document category (legacy fallback)
            service_request_id: Optional service request ID (legacy)
            company_name: Company name for top-level folder organization
            username: Username for folder organization
            service_name: Service name for folder organization

        Returns:
            dict with success status and file info
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Zoho Drive not configured'}

        try:
            parent_id = self.root_folder_id

            if company_name:
                # New organized structure: root/company/username/service/
                company_folder_name = self._sanitize_folder_name(company_name)
                parent_id = self._get_or_create_folder(parent_id, company_folder_name)
                if not parent_id:
                    return {'success': False, 'error': 'Failed to create company folder'}

                # Create username folder
                user_folder_name = self._sanitize_folder_name(username) if username else 'Unknown_User'
                parent_id = self._get_or_create_folder(parent_id, user_folder_name)
                if not parent_id:
                    return {'success': False, 'error': 'Failed to create user folder'}

                # Create service folder
                service_folder_name = self._sanitize_folder_name(service_name) if service_name else category
                parent_id = self._get_or_create_folder(parent_id, service_folder_name)
                if not parent_id:
                    return {'success': False, 'error': 'Failed to create service folder'}
            else:
                # Legacy folder path: root/client_name/[service_request_id/]category/
                # Create client folder
                if client_name:
                    client_folder_name = self._sanitize_folder_name(client_name)
                    parent_id = self._get_or_create_folder(parent_id, client_folder_name)
                    if not parent_id:
                        return {'success': False, 'error': 'Failed to create client folder'}

                # Create service request folder if provided
                if service_request_id:
                    parent_id = self._get_or_create_folder(parent_id, str(service_request_id))
                    if not parent_id:
                        return {'success': False, 'error': 'Failed to create request folder'}

                # Create category folder
                parent_id = self._get_or_create_folder(parent_id, category)
                if not parent_id:
                    return {'success': False, 'error': 'Failed to create category folder'}

            # Generate unique filename
            unique_id = str(uuid.uuid4())
            file_ext = os.path.splitext(original_filename)[1].lower()
            stored_filename = f'{unique_id}{file_ext}'

            # Upload file
            headers = {
                'Authorization': f'Zoho-oauthtoken {self.access_token}'
            }

            file_stream.seek(0)
            file_content = file_stream.read()
            file_size = len(file_content)
            file_stream.seek(0)

            upload_url = f'{self.BASE_URL}/upload'
            files = {
                'content': (stored_filename, file_stream, 'application/octet-stream')
            }
            data = {
                'parent_id': parent_id,
                'filename': stored_filename,
                'override-name-exist': 'false'
            }

            response = requests.post(upload_url, headers=headers, files=files, data=data)

            if response.status_code in [200, 201]:
                result = response.json()
                file_data = result.get('data', [{}])[0] if isinstance(result.get('data'), list) else result.get('data', {})
                file_id = file_data.get('attributes', {}).get('resource_id') or file_data.get('id')

                # Build blob_name for reference
                blob_name_parts = []
                if company_name:
                    # New organized structure
                    blob_name_parts.append(company_name)
                    blob_name_parts.append(username if username else 'Unknown_User')
                    blob_name_parts.append(service_name if service_name else category)
                else:
                    # Legacy structure
                    if client_name:
                        blob_name_parts.append(client_name)
                    if service_request_id:
                        blob_name_parts.append(str(service_request_id))
                    blob_name_parts.append(category)
                blob_name_parts.append(stored_filename)
                blob_name = '/'.join(blob_name_parts)

                return {
                    'success': True,
                    'stored_filename': stored_filename,
                    'blob_name': blob_name,
                    'file_size': file_size,
                    'zoho_file_id': file_id,
                    'zoho_permalink': file_data.get('attributes', {}).get('permalink', ''),
                    'sharepoint_item_id': file_id  # Use same field for compatibility
                }
            else:
                return {'success': False, 'error': f'Upload failed: {response.text}'}

        except Exception as e:
            current_app.logger.error(f'Zoho Drive upload error: {str(e)}')
            return {'success': False, 'error': str(e)}

    def get_download_url(self, file_id, expiry_hours=1):
        """
        Get download URL for a file.

        Args:
            file_id: Zoho file ID
            expiry_hours: How long the link should be valid

        Returns:
            dict with download URL
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Zoho Drive not configured'}

        try:
            headers = self._get_headers()
            url = f'{self.BASE_URL}/files/{file_id}/download'

            response = requests.get(url, headers=headers, allow_redirects=False)

            if response.status_code == 302:
                download_url = response.headers.get('Location')
                return {
                    'success': True,
                    'download_url': download_url
                }
            elif response.status_code == 200:
                # Some endpoints return the URL in response body
                return {
                    'success': True,
                    'download_url': f'{self.BASE_URL}/files/{file_id}/download'
                }
            else:
                return {'success': False, 'error': f'Failed to get download URL: {response.text}'}

        except Exception as e:
            current_app.logger.error(f'Zoho get download URL error: {str(e)}')
            return {'success': False, 'error': str(e)}

    def get_view_url(self, file_id, expiry_hours=24):
        """Get view URL for a file (same as download for Zoho)"""
        return self.get_download_url(file_id, expiry_hours)

    def delete_file(self, file_id):
        """
        Delete a file from Zoho Drive (move to trash).

        Args:
            file_id: Zoho file ID

        Returns:
            dict with success status
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Zoho Drive not configured'}

        try:
            headers = self._get_headers()
            url = f'{self.BASE_URL}/files/{file_id}'

            response = requests.delete(url, headers=headers)

            if response.status_code in [200, 204]:
                return {'success': True}
            else:
                return {'success': False, 'error': f'Delete failed: {response.text}'}

        except Exception as e:
            current_app.logger.error(f'Zoho delete file error: {str(e)}')
            return {'success': False, 'error': str(e)}

    def create_sharing_link(self, file_id, link_type='view', scope='anyone', expiry_hours=168):
        """
        Create a sharing link for a file.

        Args:
            file_id: Zoho file ID
            link_type: 'view' or 'edit'
            scope: 'anyone' or 'organization'
            expiry_hours: Link expiry in hours

        Returns:
            dict with sharing link
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Zoho Drive not configured'}

        try:
            headers = self._get_headers()
            url = f'{self.BASE_URL}/files/{file_id}/links'

            payload = {
                'data': {
                    'attributes': {
                        'link_name': f'Share_{file_id[:8]}',
                        'request_user_data': False,
                        'allow_download': True,
                        'role_id': '34' if link_type == 'view' else '33'  # Zoho role IDs
                    },
                    'type': 'links'
                }
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                data = response.json()
                link = data.get('data', {}).get('attributes', {}).get('link', '')
                return {
                    'success': True,
                    'link': link
                }
            else:
                return {'success': False, 'error': f'Failed to create sharing link: {response.text}'}

        except Exception as e:
            current_app.logger.error(f'Zoho create sharing link error: {str(e)}')
            return {'success': False, 'error': str(e)}

    def test_connection(self):
        """Test Zoho Drive connection"""
        if not self.is_configured():
            return {'success': False, 'error': 'Zoho Drive not configured'}

        try:
            self._ensure_valid_token()

            headers = self._get_headers()
            url = f'{self.BASE_URL}/files/{self.root_folder_id}'

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return {'success': True, 'message': 'Zoho Drive connection successful'}
            else:
                return {'success': False, 'error': f'Connection test failed: {response.text}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_authorization_url(client_id, redirect_uri, state=None):
        """
        Get OAuth authorization URL for Zoho.

        Args:
            client_id: Zoho client ID
            redirect_uri: OAuth redirect URI
            state: Optional state parameter

        Returns:
            str: Authorization URL
        """
        scopes = 'WorkDrive.files.ALL,WorkDrive.team.READ'
        url = f'{ZohoDriveClient.AUTH_URL}/auth'
        params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scopes,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        if state:
            params['state'] = state

        return f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    @staticmethod
    def exchange_code_for_tokens(client_id, client_secret, code, redirect_uri):
        """
        Exchange authorization code for tokens.

        Args:
            client_id: Zoho client ID
            client_secret: Zoho client secret
            code: Authorization code
            redirect_uri: OAuth redirect URI

        Returns:
            dict with tokens
        """
        try:
            response = requests.post(
                f'{ZohoDriveClient.AUTH_URL}/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri
                }
            )

            if response.status_code == 200:
                data = response.json()
                expires_in = data.get('expires_in', 3600)
                return {
                    'success': True,
                    'access_token': data.get('access_token'),
                    'refresh_token': data.get('refresh_token'),
                    'expires_at': datetime.utcnow() + timedelta(seconds=expires_in)
                }
            else:
                return {'success': False, 'error': f'Token exchange failed: {response.text}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}
