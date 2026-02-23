"""
OneDrive Client
===============
Microsoft Graph API client for OneDrive file operations.
"""
import msal
import requests
import uuid
import os
from flask import current_app


class OneDriveClient:
    """Microsoft Graph API client for OneDrive file operations"""

    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

    def __init__(self):
        self.client_id = current_app.config.get('GRAPH_CLIENT_ID')
        self.client_secret = current_app.config.get('GRAPH_CLIENT_SECRET')
        self.tenant_id = current_app.config.get('GRAPH_TENANT_ID')
        self.onedrive_user_id = current_app.config.get('ONEDRIVE_USER_ID')
        self.root_folder = current_app.config.get('ONEDRIVE_FOLDER', 'CRM_Documents')

    def _get_access_token(self):
        """Get access token using client credentials flow"""
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError('Graph API credentials not configured')

        authority = f'https://login.microsoftonline.com/{self.tenant_id}'

        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )

        result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

        if 'access_token' in result:
            return result['access_token']
        else:
            raise Exception(f"Failed to get token: {result.get('error_description', 'Unknown error')}")

    def _get_headers(self):
        """Get authorization headers"""
        access_token = self._get_access_token()
        return {
            'Authorization': f'Bearer {access_token}'
        }

    def _ensure_folder_exists(self, folder_path):
        """Ensure a folder exists in OneDrive, create if not"""
        try:
            headers = self._get_headers()

            # Check if folder exists
            check_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{folder_path}'
            response = requests.get(check_url, headers=headers)

            if response.status_code == 200:
                return response.json().get('id')

            # Create folder if it doesn't exist
            parts = folder_path.split('/')
            current_path = ''

            for part in parts:
                parent_path = current_path if current_path else 'root'
                current_path = f'{current_path}/{part}' if current_path else part

                # Check if this part exists
                if parent_path == 'root':
                    check_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{current_path}'
                else:
                    check_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{current_path}'

                response = requests.get(check_url, headers=headers)

                if response.status_code != 200:
                    # Create folder
                    if parent_path == 'root':
                        create_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root/children'
                    else:
                        create_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{parent_path}:/children'

                    folder_data = {
                        'name': part,
                        'folder': {},
                        '@microsoft.graph.conflictBehavior': 'replace'
                    }

                    headers_json = {**headers, 'Content-Type': 'application/json'}
                    create_response = requests.post(create_url, headers=headers_json, json=folder_data)

                    if create_response.status_code not in [200, 201]:
                        current_app.logger.error(f'Failed to create folder: {create_response.text}')

            # Get final folder ID
            final_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{folder_path}'
            final_response = requests.get(final_url, headers=headers)

            if final_response.status_code == 200:
                return final_response.json().get('id')

            return None

        except Exception as e:
            current_app.logger.error(f'Error ensuring folder exists: {str(e)}')
            return None

    def upload_file(self, file_stream, original_filename, service_request_id=None, category='supporting_document'):
        """
        Upload a file to OneDrive

        Args:
            file_stream: File stream/bytes to upload
            original_filename: Original filename
            service_request_id: Optional service request ID for organizing
            category: Document category for organizing

        Returns:
            dict with onedrive_item_id, onedrive_url, onedrive_web_url, stored_filename
        """
        try:
            # Generate unique filename
            file_ext = os.path.splitext(original_filename)[1].lower()
            unique_id = str(uuid.uuid4())
            stored_filename = f'{unique_id}{file_ext}'

            # Build folder path
            if service_request_id:
                folder_path = f'{self.root_folder}/requests/{service_request_id}/{category}'
            else:
                folder_path = f'{self.root_folder}/general/{category}'

            # Ensure folder exists
            self._ensure_folder_exists(folder_path)

            # Get file content
            if hasattr(file_stream, 'read'):
                file_content = file_stream.read()
            else:
                file_content = file_stream

            file_size = len(file_content)

            headers = self._get_headers()

            # For files smaller than 4MB, use simple upload
            if file_size < 4 * 1024 * 1024:
                upload_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{folder_path}/{stored_filename}:/content'

                headers['Content-Type'] = 'application/octet-stream'
                response = requests.put(upload_url, headers=headers, data=file_content)

                if response.status_code in [200, 201]:
                    result = response.json()
                    return {
                        'success': True,
                        'onedrive_item_id': result.get('id'),
                        'onedrive_url': result.get('@microsoft.graph.downloadUrl'),
                        'onedrive_web_url': result.get('webUrl'),
                        'stored_filename': stored_filename,
                        'file_size': file_size
                    }
                else:
                    current_app.logger.error(f'OneDrive upload failed: {response.text}')
                    return {
                        'success': False,
                        'error': f'Upload failed: {response.status_code}'
                    }
            else:
                # For larger files, use upload session
                return self._upload_large_file(file_content, folder_path, stored_filename)

        except Exception as e:
            current_app.logger.error(f'Error uploading to OneDrive: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _upload_large_file(self, file_content, folder_path, stored_filename):
        """Upload large files using upload session"""
        try:
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'

            # Create upload session
            session_url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/root:/{folder_path}/{stored_filename}:/createUploadSession'

            session_data = {
                'item': {
                    '@microsoft.graph.conflictBehavior': 'replace',
                    'name': stored_filename
                }
            }

            session_response = requests.post(session_url, headers=headers, json=session_data)

            if session_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Failed to create upload session: {session_response.status_code}'
                }

            upload_url = session_response.json().get('uploadUrl')
            file_size = len(file_content)

            # Upload in chunks (10MB chunks)
            chunk_size = 10 * 1024 * 1024
            chunks = [file_content[i:i + chunk_size] for i in range(0, file_size, chunk_size)]

            result = None
            start_byte = 0

            for chunk in chunks:
                end_byte = start_byte + len(chunk) - 1

                chunk_headers = {
                    'Content-Length': str(len(chunk)),
                    'Content-Range': f'bytes {start_byte}-{end_byte}/{file_size}'
                }

                chunk_response = requests.put(upload_url, headers=chunk_headers, data=chunk)

                if chunk_response.status_code in [200, 201]:
                    result = chunk_response.json()
                elif chunk_response.status_code != 202:
                    return {
                        'success': False,
                        'error': f'Chunk upload failed: {chunk_response.status_code}'
                    }

                start_byte = end_byte + 1

            if result:
                return {
                    'success': True,
                    'onedrive_item_id': result.get('id'),
                    'onedrive_url': result.get('@microsoft.graph.downloadUrl'),
                    'onedrive_web_url': result.get('webUrl'),
                    'stored_filename': stored_filename,
                    'file_size': file_size
                }

            return {
                'success': False,
                'error': 'Upload completed but no result returned'
            }

        except Exception as e:
            current_app.logger.error(f'Error in large file upload: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_download_url(self, item_id):
        """Get a fresh download URL for a file"""
        try:
            headers = self._get_headers()

            url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/items/{item_id}'
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'download_url': result.get('@microsoft.graph.downloadUrl'),
                    'web_url': result.get('webUrl')
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to get download URL: {response.status_code}'
                }

        except Exception as e:
            current_app.logger.error(f'Error getting download URL: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def create_sharing_link(self, item_id, link_type='view', scope='anonymous'):
        """
        Create a sharing link for a file

        Args:
            item_id: OneDrive item ID
            link_type: 'view' or 'edit'
            scope: 'anonymous' or 'organization'

        Returns:
            dict with sharing link URL
        """
        try:
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'

            url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/items/{item_id}/createLink'

            link_data = {
                'type': link_type,
                'scope': scope
            }

            response = requests.post(url, headers=headers, json=link_data)

            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'link': result.get('link', {}).get('webUrl')
                }
            else:
                current_app.logger.error(f'Failed to create sharing link: {response.text}')
                return {
                    'success': False,
                    'error': f'Failed to create link: {response.status_code}'
                }

        except Exception as e:
            current_app.logger.error(f'Error creating sharing link: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, item_id):
        """Delete a file from OneDrive"""
        try:
            headers = self._get_headers()

            url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/items/{item_id}'
            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'error': f'Delete failed: {response.status_code}'
                }

        except Exception as e:
            current_app.logger.error(f'Error deleting file: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_file_metadata(self, item_id):
        """Get file metadata from OneDrive"""
        try:
            headers = self._get_headers()

            url = f'{self.GRAPH_API_ENDPOINT}/users/{self.onedrive_user_id}/drive/items/{item_id}'
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return {
                    'success': True,
                    'metadata': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to get metadata: {response.status_code}'
                }

        except Exception as e:
            current_app.logger.error(f'Error getting file metadata: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
