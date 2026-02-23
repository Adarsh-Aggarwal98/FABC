"""
Google Apps Script Client for document storage
Uses a deployed Google Apps Script Web App to upload files to Google Drive
This bypasses OAuth complexity - the script runs with deployer's permissions
"""
import os
import base64
import requests
from flask import current_app


class GoogleAppsScriptClient:
    """Client for uploading files via Google Apps Script Web App"""

    def __init__(self, web_app_url=None, root_folder_id=None):
        """
        Initialize Google Apps Script client.

        Args:
            web_app_url: The deployed Google Apps Script Web App URL
            root_folder_id: Optional root folder ID in Google Drive
        """
        self.web_app_url = web_app_url or current_app.config.get('GOOGLE_APPS_SCRIPT_URL')
        self.root_folder_id = root_folder_id or current_app.config.get('GOOGLE_APPS_SCRIPT_FOLDER_ID', '')

    def is_configured(self):
        """Check if Google Apps Script is properly configured"""
        return bool(self.web_app_url)

    def _sanitize_folder_name(self, name):
        """Sanitize a name for use as a Google Drive folder name."""
        if not name:
            return 'Unknown'

        import re
        # Allow alphanumeric, spaces, hyphens, underscores
        safe_name = ''.join(c for c in name if c.isalnum() or c in ' -_').strip()
        safe_name = re.sub(r'\s+', ' ', safe_name)

        if len(safe_name) > 128:
            safe_name = safe_name[:128]

        return safe_name or 'Unknown'

    def upload_file(self, file_stream, original_filename, client_name=None,
                    category='supporting_document', service_request_id=None,
                    company_name=None, username=None, service_name=None):
        """
        Upload a file to Google Drive via Apps Script Web App.

        Args:
            file_stream: File-like object with the file content
            original_filename: Original name of the file
            client_name: Name of the client (legacy)
            category: Document category
            service_request_id: Optional service request ID
            company_name: Company name for folder organization
            username: Username for folder organization
            service_name: Service name for folder organization

        Returns:
            dict with file_id and other metadata
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Google Apps Script not configured'
            }

        try:
            # Read file content and encode as base64
            file_content = file_stream.read() if hasattr(file_stream, 'read') else file_stream
            file_base64 = base64.b64encode(file_content).decode('utf-8')

            # Build folder path
            folder_path_parts = []

            if company_name:
                folder_path_parts.append(self._sanitize_folder_name(company_name))
                if username:
                    folder_path_parts.append(self._sanitize_folder_name(username))
                if service_name:
                    folder_path_parts.append(self._sanitize_folder_name(service_name))
            elif client_name:
                folder_path_parts.append(self._sanitize_folder_name(client_name))
                if category:
                    folder_path_parts.append(category)

            folder_path = '/'.join(folder_path_parts) if folder_path_parts else ''

            # Prepare payload
            payload = {
                'action': 'upload',
                'filename': original_filename,
                'content': file_base64,
                'folderPath': folder_path,
                'rootFolderId': self.root_folder_id,
                'metadata': {
                    'service_request_id': service_request_id,
                    'category': category,
                    'company_name': company_name,
                    'username': username
                }
            }

            # Send to Apps Script Web App
            response = requests.post(
                self.web_app_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Allow longer timeout for file uploads
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Apps Script returned status {response.status_code}: {response.text[:200]}'
                }

            result = response.json()

            if result.get('success'):
                return {
                    'success': True,
                    'file_id': result.get('fileId'),
                    'file_name': result.get('fileName', original_filename),
                    'web_view_link': result.get('webViewLink'),
                    'web_content_link': result.get('webContentLink'),
                    'size': result.get('size', len(file_content)),
                    'mime_type': result.get('mimeType'),
                    'provider': 'GOOGLE_APPS_SCRIPT'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error from Apps Script')
                }

        except requests.exceptions.Timeout:
            current_app.logger.error('Google Apps Script upload timeout')
            return {
                'success': False,
                'error': 'Upload timeout - file may be too large'
            }
        except Exception as e:
            current_app.logger.error(f'Google Apps Script upload error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_download_url(self, file_id):
        """
        Get download URL for a file.

        Args:
            file_id: Google Drive file ID

        Returns:
            dict with download URL
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Google Apps Script not configured'
            }

        try:
            response = requests.post(
                self.web_app_url,
                json={
                    'action': 'getDownloadUrl',
                    'fileId': file_id
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Apps Script returned status {response.status_code}'
                }

            result = response.json()

            if result.get('success'):
                return {
                    'success': True,
                    'download_url': result.get('downloadUrl'),
                    'web_view_link': result.get('webViewLink'),
                    'file_name': result.get('fileName'),
                    'mime_type': result.get('mimeType')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }

        except Exception as e:
            current_app.logger.error(f'Google Apps Script get download URL error: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, file_id):
        """
        Delete a file from Google Drive.

        Args:
            file_id: Google Drive file ID

        Returns:
            dict with success status
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Google Apps Script not configured'
            }

        try:
            response = requests.post(
                self.web_app_url,
                json={
                    'action': 'delete',
                    'fileId': file_id
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Apps Script returned status {response.status_code}'
                }

            result = response.json()
            return {
                'success': result.get('success', False),
                'error': result.get('error')
            }

        except Exception as e:
            current_app.logger.error(f'Google Apps Script delete error: {str(e)}')
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
            return []

        try:
            response = requests.post(
                self.web_app_url,
                json={
                    'action': 'listFiles',
                    'folderId': folder_id or self.root_folder_id,
                    'pageSize': page_size
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code != 200:
                return []

            result = response.json()
            return result.get('files', [])

        except Exception as e:
            current_app.logger.error(f'Google Apps Script list files error: {str(e)}')
            return []

    def test_connection(self):
        """
        Test connection to Google Apps Script.

        Returns:
            dict with success status
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Google Apps Script URL not configured'
            }

        try:
            response = requests.post(
                self.web_app_url,
                json={'action': 'test'},
                headers={'Content-Type': 'application/json'},
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': result.get('success', True),
                    'message': result.get('message', 'Google Apps Script connection successful'),
                    'email': result.get('email')
                }
            else:
                return {
                    'success': False,
                    'error': f'Apps Script returned status {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
