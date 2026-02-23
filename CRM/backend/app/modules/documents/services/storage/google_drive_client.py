"""
Google Drive Client for document storage
Provides file upload, download, and management functionality using Google Drive API
"""
import os
import io
import json
import requests
from datetime import datetime, timedelta
from flask import current_app
from urllib.parse import urlencode


class GoogleDriveClient:
    """Client for interacting with Google Drive API"""

    # Google OAuth2 endpoints
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    API_URL = 'https://www.googleapis.com/drive/v3'
    UPLOAD_URL = 'https://www.googleapis.com/upload/drive/v3'

    # Required OAuth2 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',  # Create/access files created by app
        'https://www.googleapis.com/auth/drive.metadata.readonly'  # View file metadata
    ]

    def __init__(self, config=None):
        """
        Initialize Google Drive client with configuration.

        Args:
            config: Either a CompanyStorageConfig object or a dict with Google Drive settings
        """
        self.config = config
        self._extract_settings()

    def _extract_settings(self):
        """Extract Google Drive settings from config"""
        if self.config is None:
            self.client_id = None
            self.client_secret = None
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            self.root_folder_id = None
            return

        if hasattr(self.config, 'google_client_id'):
            # It's a model object
            self.client_id = self.config.google_client_id
            self.client_secret = self.config.google_client_secret
            self.access_token = self.config.google_access_token
            self.refresh_token = self.config.google_refresh_token
            self.token_expires_at = self.config.google_token_expires_at
            self.root_folder_id = self.config.google_root_folder_id
        else:
            # It's a dict
            self.client_id = self.config.get('google_client_id')
            self.client_secret = self.config.get('google_client_secret')
            self.access_token = self.config.get('google_access_token')
            self.refresh_token = self.config.get('google_refresh_token')
            self.token_expires_at = self.config.get('google_token_expires_at')
            self.root_folder_id = self.config.get('google_root_folder_id')

    def is_configured(self):
        """Check if Google Drive is properly configured"""
        return all([
            self.client_id,
            self.client_secret,
            self.access_token or self.refresh_token
        ])

    def _get_headers(self):
        """Get authorization headers"""
        self._ensure_valid_token()
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _ensure_valid_token(self):
        """Ensure access token is valid, refresh if necessary"""
        if self.token_expires_at:
            if isinstance(self.token_expires_at, str):
                self.token_expires_at = datetime.fromisoformat(self.token_expires_at)
            if datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5):
                self._refresh_access_token()

    def _refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            raise Exception('No refresh token available')

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }

        response = requests.post(self.TOKEN_URL, data=data)
        if response.status_code != 200:
            raise Exception(f'Failed to refresh token: {response.text}')

        token_data = response.json()
        self.access_token = token_data['access_token']
        expires_in = token_data.get('expires_in', 3600)
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Update config if it's a model object
        if hasattr(self.config, 'google_access_token'):
            self.config.google_access_token = self.access_token
            self.config.google_token_expires_at = self.token_expires_at

    def _get_or_create_folder(self, folder_name, parent_id=None):
        """Get or create a folder by name"""
        # Search for existing folder
        parent_clause = f"'{parent_id}' in parents" if parent_id else f"'{self.root_folder_id}' in parents"
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and {parent_clause} and trashed=false"

        response = requests.get(
            f'{self.API_URL}/files',
            headers=self._get_headers(),
            params={'q': query, 'fields': 'files(id,name)'}
        )

        if response.status_code == 200:
            files = response.json().get('files', [])
            if files:
                return files[0]['id']

        # Create folder if not found
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id or self.root_folder_id] if (parent_id or self.root_folder_id) else []
        }

        response = requests.post(
            f'{self.API_URL}/files',
            headers=self._get_headers(),
            json=metadata
        )

        if response.status_code not in [200, 201]:
            raise Exception(f'Failed to create folder: {response.text}')

        return response.json()['id']

    def _sanitize_folder_name(self, name):
        """
        Sanitize a name for use as a Google Drive folder name.
        """
        if not name:
            return 'Unknown'

        # Allow alphanumeric, spaces, hyphens, underscores
        safe_name = ''.join(c for c in name if c.isalnum() or c in ' -_').strip()

        # Replace multiple spaces with single space
        import re
        safe_name = re.sub(r'\s+', ' ', safe_name)

        # Limit length
        if len(safe_name) > 128:
            safe_name = safe_name[:128]

        return safe_name or 'Unknown'

    def upload_file(self, file_stream, original_filename, client_name=None,
                    category='supporting_document', service_request_id=None,
                    company_name=None, username=None, service_name=None):
        """
        Upload a file to Google Drive with organized folder structure.

        Folder structure: root/{company_name}/{username}/{service_name}/{filename}
        Falls back to legacy structure if new parameters not provided.

        Args:
            file_stream: File-like object with the file content
            original_filename: Original name of the file
            client_name: Name of the client (legacy - for folder organization)
            category: Document category (legacy fallback)
            service_request_id: Optional service request ID (legacy)
            company_name: Company name for top-level folder organization
            username: Username for folder organization
            service_name: Service name for folder organization

        Returns:
            dict with file_id and other metadata
        """
        if not self.is_configured():
            raise Exception('Google Drive not configured')

        try:
            # Determine folder structure based on available info
            parent_folder_id = self.root_folder_id

            if company_name:
                # New organized structure: root/company/username/service/
                safe_company = self._sanitize_folder_name(company_name)
                parent_folder_id = self._get_or_create_folder(safe_company, parent_folder_id)

                safe_username = self._sanitize_folder_name(username) if username else 'Unknown_User'
                parent_folder_id = self._get_or_create_folder(safe_username, parent_folder_id)

                safe_service = self._sanitize_folder_name(service_name) if service_name else category
                parent_folder_id = self._get_or_create_folder(safe_service, parent_folder_id)
            else:
                # Legacy structure: root/client_name/category/
                if client_name:
                    safe_client_name = self._sanitize_folder_name(client_name)
                    if safe_client_name:
                        parent_folder_id = self._get_or_create_folder(safe_client_name, parent_folder_id)

                if category:
                    parent_folder_id = self._get_or_create_folder(category, parent_folder_id)

            # Read file content
            file_content = file_stream.read() if hasattr(file_stream, 'read') else file_stream

            # Prepare metadata
            metadata = {
                'name': original_filename,
                'parents': [parent_folder_id] if parent_folder_id else []
            }

            # Add custom properties
            if service_request_id:
                metadata['appProperties'] = {
                    'service_request_id': str(service_request_id),
                    'category': category
                }

            # Upload file using multipart upload
            boundary = '-------314159265358979323846'
            delimiter = f'\r\n--{boundary}\r\n'
            close_delim = f'\r\n--{boundary}--'

            body = (
                delimiter +
                'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
                json.dumps(metadata) +
                delimiter +
                f'Content-Type: application/octet-stream\r\n\r\n'
            ).encode('utf-8') + file_content + close_delim.encode('utf-8')

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': f'multipart/related; boundary="{boundary}"'
            }

            response = requests.post(
                f'{self.UPLOAD_URL}/files?uploadType=multipart&fields=id,name,webViewLink,size,mimeType',
                headers=headers,
                data=body
            )

            if response.status_code not in [200, 201]:
                raise Exception(f'Upload failed: {response.text}')

            file_data = response.json()

            return {
                'success': True,
                'file_id': file_data['id'],
                'file_name': file_data['name'],
                'web_view_link': file_data.get('webViewLink'),
                'size': file_data.get('size'),
                'mime_type': file_data.get('mimeType'),
                'provider': 'GOOGLE_DRIVE'
            }

        except Exception as e:
            current_app.logger.error(f'Google Drive upload error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_download_url(self, file_id, expiry_hours=1):
        """
        Get a download URL for a file.
        Note: For Google Drive, we return the webContentLink or create a shareable link.

        Args:
            file_id: Google Drive file ID
            expiry_hours: Not used for Google Drive (links don't expire the same way)

        Returns:
            dict with download URL
        """
        if not self.is_configured():
            raise Exception('Google Drive not configured')

        try:
            # Get file metadata including download link
            response = requests.get(
                f'{self.API_URL}/files/{file_id}',
                headers=self._get_headers(),
                params={'fields': 'id,name,webContentLink,webViewLink,mimeType'}
            )

            if response.status_code != 200:
                raise Exception(f'Failed to get file: {response.text}')

            file_data = response.json()

            # webContentLink is the direct download link
            download_url = file_data.get('webContentLink')

            if not download_url:
                # For non-binary files, use export link or create permission
                download_url = f'{self.API_URL}/files/{file_id}?alt=media'

            return {
                'success': True,
                'download_url': download_url,
                'web_view_link': file_data.get('webViewLink'),
                'file_name': file_data.get('name'),
                'mime_type': file_data.get('mimeType')
            }

        except Exception as e:
            current_app.logger.error(f'Google Drive get download URL error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def download_file(self, file_id):
        """
        Download a file from Google Drive.

        Args:
            file_id: Google Drive file ID

        Returns:
            File content as bytes
        """
        if not self.is_configured():
            raise Exception('Google Drive not configured')

        headers = self._get_headers()
        response = requests.get(
            f'{self.API_URL}/files/{file_id}',
            headers=headers,
            params={'alt': 'media'}
        )

        if response.status_code != 200:
            raise Exception(f'Failed to download file: {response.text}')

        return response.content

    def delete_file(self, file_id):
        """
        Delete a file from Google Drive.

        Args:
            file_id: Google Drive file ID

        Returns:
            dict with success status
        """
        if not self.is_configured():
            raise Exception('Google Drive not configured')

        try:
            response = requests.delete(
                f'{self.API_URL}/files/{file_id}',
                headers=self._get_headers()
            )

            if response.status_code not in [200, 204]:
                raise Exception(f'Failed to delete file: {response.text}')

            return {'success': True}

        except Exception as e:
            current_app.logger.error(f'Google Drive delete error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def list_files(self, folder_id=None, page_size=100):
        """
        List files in a folder.

        Args:
            folder_id: Folder ID (defaults to root folder)
            page_size: Number of files to return

        Returns:
            List of file metadata
        """
        if not self.is_configured():
            raise Exception('Google Drive not configured')

        parent_id = folder_id or self.root_folder_id
        query = f"'{parent_id}' in parents and trashed=false" if parent_id else "trashed=false"

        response = requests.get(
            f'{self.API_URL}/files',
            headers=self._get_headers(),
            params={
                'q': query,
                'pageSize': page_size,
                'fields': 'files(id,name,mimeType,size,createdTime,modifiedTime,webViewLink)'
            }
        )

        if response.status_code != 200:
            raise Exception(f'Failed to list files: {response.text}')

        return response.json().get('files', [])

    def create_sharing_link(self, file_id, role='reader', type='anyone'):
        """
        Create a sharing link for a file.

        Args:
            file_id: Google Drive file ID
            role: Permission role ('reader', 'writer', 'commenter')
            type: Permission type ('user', 'group', 'domain', 'anyone')

        Returns:
            dict with sharing link
        """
        if not self.is_configured():
            raise Exception('Google Drive not configured')

        try:
            # Create permission
            permission = {
                'role': role,
                'type': type
            }

            response = requests.post(
                f'{self.API_URL}/files/{file_id}/permissions',
                headers=self._get_headers(),
                json=permission
            )

            if response.status_code not in [200, 201]:
                raise Exception(f'Failed to create permission: {response.text}')

            # Get the file's web view link
            file_response = requests.get(
                f'{self.API_URL}/files/{file_id}',
                headers=self._get_headers(),
                params={'fields': 'webViewLink,webContentLink'}
            )

            if file_response.status_code == 200:
                file_data = file_response.json()
                return {
                    'success': True,
                    'web_view_link': file_data.get('webViewLink'),
                    'web_content_link': file_data.get('webContentLink')
                }

            return {'success': True}

        except Exception as e:
            current_app.logger.error(f'Google Drive create sharing link error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def test_connection(self):
        """
        Test connection to Google Drive.

        Returns:
            dict with success status
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Google Drive not configured properly'
            }

        try:
            # Try to get user info
            response = requests.get(
                'https://www.googleapis.com/drive/v3/about',
                headers=self._get_headers(),
                params={'fields': 'user,storageQuota'}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': 'Google Drive connection successful',
                    'user': data.get('user', {}).get('emailAddress'),
                    'storage_quota': data.get('storageQuota')
                }

            return {
                'success': False,
                'error': f'API returned status {response.status_code}: {response.text}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_authorization_url(client_id, redirect_uri, state=None):
        """
        Generate OAuth2 authorization URL for Google Drive.

        Args:
            client_id: Google OAuth client ID
            redirect_uri: Redirect URI for OAuth callback
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL
        """
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(GoogleDriveClient.SCOPES),
            'response_type': 'code',
            'access_type': 'offline',  # Required for refresh token
            'prompt': 'consent',  # Force consent to get refresh token
        }

        if state:
            params['state'] = state

        return f'{GoogleDriveClient.AUTH_URL}?{urlencode(params)}'

    @staticmethod
    def exchange_code_for_tokens(client_id, client_secret, code, redirect_uri):
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI (must match the one used in authorization)

        Returns:
            dict with access_token, refresh_token, and expires_at
        """
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        response = requests.post(GoogleDriveClient.TOKEN_URL, data=data)

        if response.status_code != 200:
            raise Exception(f'Failed to exchange code: {response.text}')

        token_data = response.json()
        expires_in = token_data.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'expires_at': expires_at,
            'token_type': token_data.get('token_type', 'Bearer')
        }
