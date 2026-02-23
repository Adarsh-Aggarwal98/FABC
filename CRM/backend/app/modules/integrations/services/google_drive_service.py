"""
Google Drive Service

OAuth 2.0 client and API wrapper for Google Drive integration.
This service handles document storage on Google Drive.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class GoogleDriveConfig:
    """Google Drive configuration from environment variables"""

    CLIENT_ID = os.environ.get('GOOGLE_DRIVE_CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('GOOGLE_DRIVE_CLIENT_SECRET', '')
    REDIRECT_URI = os.environ.get('GOOGLE_DRIVE_REDIRECT_URI', 'http://localhost:5001/api/integrations/google-drive/callback')
    ACCESS_TOKEN = os.environ.get('GOOGLE_DRIVE_ACCESS_TOKEN', '')
    REFRESH_TOKEN = os.environ.get('GOOGLE_DRIVE_REFRESH_TOKEN', '')
    ROOT_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_ROOT_FOLDER_ID', '')

    # Google OAuth endpoints
    AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'

    # Google Drive API
    API_BASE_URL = 'https://www.googleapis.com/drive/v3'
    UPLOAD_URL = 'https://www.googleapis.com/upload/drive/v3'

    # OAuth scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]

    @classmethod
    def is_configured(cls) -> bool:
        """Check if Google Drive integration is properly configured"""
        return bool(cls.CLIENT_ID and cls.CLIENT_SECRET)

    @classmethod
    def is_authorized(cls) -> bool:
        """Check if Google Drive is authorized (has tokens)"""
        return bool(cls.ACCESS_TOKEN or cls.REFRESH_TOKEN)


class GoogleDriveAuthClient:
    """
    Handles Google OAuth 2.0 authentication flow.
    """

    def __init__(self):
        if not GoogleDriveConfig.is_configured():
            logger.warning("Google Drive integration not configured.")

    @staticmethod
    def get_authorization_url(client_id: str, redirect_uri: str, state: str) -> str:
        """
        Generate the Google authorization URL.

        Args:
            client_id: OAuth client ID
            redirect_uri: Callback URL
            state: CSRF protection state

        Returns:
            Authorization URL to redirect the user to
        """
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(GoogleDriveConfig.SCOPES),
            'access_type': 'offline',  # Required to get refresh token
            'prompt': 'consent',  # Force consent to get refresh token
            'state': state
        }
        return f"{GoogleDriveConfig.AUTHORIZE_URL}?{urlencode(params)}"

    @staticmethod
    def exchange_code_for_tokens(
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            code: Authorization code
            redirect_uri: Callback URL

        Returns:
            Token response
        """
        try:
            response = requests.post(
                GoogleDriveConfig.TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully exchanged code for Google tokens")
                return token_data
            else:
                logger.error(f"Failed to exchange code: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            return None

    @staticmethod
    def refresh_access_token(
        client_id: str,
        client_secret: str,
        refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Refresh the access token using refresh token.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            refresh_token: Valid refresh token

        Returns:
            New token response
        """
        try:
            response = requests.post(
                GoogleDriveConfig.TOKEN_URL,
                data={
                    'grant_type': 'refresh_token',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'refresh_token': refresh_token
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                logger.info("Successfully refreshed Google access token")
                return token_data
            else:
                logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None


class GoogleDriveAPIClient:
    """
    Google Drive API client for file operations.
    """

    def __init__(self, config: Dict[str, str]):
        """
        Initialize Google Drive API client.

        Args:
            config: Configuration dictionary with keys:
                - google_client_id
                - google_client_secret
                - google_access_token
                - google_refresh_token
                - google_root_folder_id (optional)
        """
        self.config = config
        self.access_token = config.get('google_access_token', '')
        self.refresh_token = config.get('google_refresh_token', '')
        self.client_id = config.get('google_client_id', '')
        self.client_secret = config.get('google_client_secret', '')
        self.root_folder_id = config.get('google_root_folder_id', '')

    def is_configured(self) -> bool:
        """Check if client is configured with tokens"""
        return bool(self.access_token or self.refresh_token)

    def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        if not self.access_token and self.refresh_token:
            token_data = GoogleDriveAuthClient.refresh_access_token(
                self.client_id,
                self.client_secret,
                self.refresh_token
            )
            if token_data:
                self.access_token = token_data.get('access_token', '')
                return True
            return False
        return bool(self.access_token)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

    def test_connection(self) -> Dict[str, Any]:
        """Test the Google Drive connection"""
        if not self._ensure_valid_token():
            return {'success': False, 'error': 'Failed to get valid access token'}

        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=self._get_headers()
            )

            if response.status_code == 200:
                user_info = response.json()
                return {
                    'success': True,
                    'user': {
                        'email': user_info.get('email'),
                        'name': user_info.get('name')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_files(self, folder_id: str = None, page_size: int = 100) -> List[Dict]:
        """
        List files in a folder.

        Args:
            folder_id: Parent folder ID (uses root if not specified)
            page_size: Number of files to return

        Returns:
            List of file metadata
        """
        if not self._ensure_valid_token():
            return []

        parent_id = folder_id or self.root_folder_id or 'root'

        try:
            params = {
                'q': f"'{parent_id}' in parents and trashed = false",
                'pageSize': page_size,
                'fields': 'files(id, name, mimeType, size, createdTime, modifiedTime)'
            }

            response = requests.get(
                f"{GoogleDriveConfig.API_BASE_URL}/files",
                headers=self._get_headers(),
                params=params
            )

            if response.status_code == 200:
                return response.json().get('files', [])
            else:
                logger.error(f"Error listing files: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []

    def create_folder(self, name: str, parent_id: str = None) -> Optional[Dict]:
        """
        Create a folder in Google Drive.

        Args:
            name: Folder name
            parent_id: Parent folder ID

        Returns:
            Folder metadata or None
        """
        if not self._ensure_valid_token():
            return None

        parent = parent_id or self.root_folder_id or 'root'

        try:
            metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent]
            }

            response = requests.post(
                f"{GoogleDriveConfig.API_BASE_URL}/files",
                headers={
                    **self._get_headers(),
                    'Content-Type': 'application/json'
                },
                json=metadata
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error creating folder: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return None

    def upload_file(
        self,
        file_path: str,
        file_name: str,
        mime_type: str,
        parent_id: str = None
    ) -> Optional[Dict]:
        """
        Upload a file to Google Drive.

        Args:
            file_path: Local file path
            file_name: Name for the file in Drive
            mime_type: MIME type of the file
            parent_id: Parent folder ID

        Returns:
            File metadata or None
        """
        if not self._ensure_valid_token():
            return None

        parent = parent_id or self.root_folder_id or 'root'

        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Create file metadata
            metadata = {
                'name': file_name,
                'parents': [parent]
            }

            # Multipart upload
            boundary = '-------314159265358979323846'
            body = (
                f'--{boundary}\r\n'
                f'Content-Type: application/json; charset=UTF-8\r\n\r\n'
                f'{str(metadata)}\r\n'
                f'--{boundary}\r\n'
                f'Content-Type: {mime_type}\r\n\r\n'
            ).encode() + file_content + f'\r\n--{boundary}--'.encode()

            response = requests.post(
                f"{GoogleDriveConfig.UPLOAD_URL}/files?uploadType=multipart",
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': f'multipart/related; boundary={boundary}'
                },
                data=body
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error uploading file: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.

        Args:
            file_id: ID of file to delete

        Returns:
            True if successful
        """
        if not self._ensure_valid_token():
            return False

        try:
            response = requests.delete(
                f"{GoogleDriveConfig.API_BASE_URL}/files/{file_id}",
                headers=self._get_headers()
            )

            return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def get_file_url(self, file_id: str) -> Optional[str]:
        """
        Get a shareable URL for a file.

        Args:
            file_id: ID of file

        Returns:
            Web view link or None
        """
        if not self._ensure_valid_token():
            return None

        try:
            response = requests.get(
                f"{GoogleDriveConfig.API_BASE_URL}/files/{file_id}",
                headers=self._get_headers(),
                params={'fields': 'webViewLink'}
            )

            if response.status_code == 200:
                return response.json().get('webViewLink')
            return None

        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            return None
