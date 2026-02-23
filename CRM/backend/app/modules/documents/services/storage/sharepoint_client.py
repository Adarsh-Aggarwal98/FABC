"""
SharePoint Client
=================
Microsoft Graph API client for SharePoint document library operations.
"""
import msal
import requests
import uuid
import os
import re
from flask import current_app


class SharePointClient:
    """Microsoft Graph API client for SharePoint document library operations"""

    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

    def __init__(self):
        self.client_id = current_app.config.get('GRAPH_CLIENT_ID')
        self.client_secret = current_app.config.get('GRAPH_CLIENT_SECRET')
        self.tenant_id = current_app.config.get('GRAPH_TENANT_ID')
        self.site_id = current_app.config.get('SHAREPOINT_SITE_ID')
        self.drive_id = current_app.config.get('SHAREPOINT_DRIVE_ID')
        self.root_folder = current_app.config.get('SHAREPOINT_ROOT_FOLDER', 'CRM_Documents')

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

    def _sanitize_folder_name(self, name):
        """
        Sanitize folder name for SharePoint compatibility.
        Removes or replaces invalid characters.
        """
        if not name:
            return 'Unknown_Client'

        # Replace invalid characters with underscore
        # SharePoint doesn't allow: " * : < > ? / \ |
        invalid_chars = r'["\*:<>\?/\\|]'
        sanitized = re.sub(invalid_chars, '_', name)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')

        # Replace multiple underscores with single
        sanitized = re.sub(r'_+', '_', sanitized)

        # Limit length to 128 characters
        if len(sanitized) > 128:
            sanitized = sanitized[:128]

        return sanitized or 'Unknown_Client'

    def _get_drive_endpoint(self):
        """Get the appropriate drive endpoint based on configuration"""
        if self.drive_id:
            return f'{self.GRAPH_API_ENDPOINT}/drives/{self.drive_id}'
        elif self.site_id:
            return f'{self.GRAPH_API_ENDPOINT}/sites/{self.site_id}/drive'
        else:
            raise ValueError('SharePoint site_id or drive_id must be configured')

    def _ensure_folder_exists(self, folder_path):
        """Ensure a folder exists in SharePoint, create if not"""
        try:
            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            # Check if folder exists
            check_url = f'{drive_endpoint}/root:/{folder_path}'
            response = requests.get(check_url, headers=headers)

            if response.status_code == 200:
                return response.json().get('id')

            # Create folder if it doesn't exist - create each level
            parts = folder_path.split('/')
            current_path = ''

            for part in parts:
                parent_path = current_path if current_path else 'root'
                current_path = f'{current_path}/{part}' if current_path else part

                # Check if this part exists
                check_url = f'{drive_endpoint}/root:/{current_path}'
                response = requests.get(check_url, headers=headers)

                if response.status_code != 200:
                    # Create folder
                    if parent_path == 'root':
                        create_url = f'{drive_endpoint}/root/children'
                    else:
                        create_url = f'{drive_endpoint}/root:/{parent_path}:/children'

                    folder_data = {
                        'name': part,
                        'folder': {},
                        '@microsoft.graph.conflictBehavior': 'replace'
                    }

                    headers_json = {**headers, 'Content-Type': 'application/json'}
                    create_response = requests.post(create_url, headers=headers_json, json=folder_data)

                    if create_response.status_code not in [200, 201]:
                        current_app.logger.error(f'Failed to create folder {part}: {create_response.text}')

            # Get final folder ID
            final_url = f'{drive_endpoint}/root:/{folder_path}'
            final_response = requests.get(final_url, headers=headers)

            if final_response.status_code == 200:
                return final_response.json().get('id')

            return None

        except Exception as e:
            current_app.logger.error(f'Error ensuring folder exists: {str(e)}')
            return None

    def upload_file(self, file_stream, original_filename, client_name=None, category='supporting_document',
                    service_request_id=None, company_name=None, username=None, service_name=None):
        """
        Upload a file to SharePoint document library with organized folder structure.

        Folder structure: {root_folder}/{username}/{service_name}/{filename}
        Folders are organized by CLIENT NAME (the user for whom data is uploaded),
        NOT by company. This allows easy browsing in SharePoint.

        Args:
            file_stream: File stream/bytes to upload
            original_filename: Original filename
            client_name: Name of the client (legacy - used if username not provided)
            category: Document category for organizing (fallback if no service_name)
            service_request_id: Optional service request ID (not used in folder path)
            company_name: Not used (kept for backward compatibility)
            username: Client/User name for folder organization (PRIMARY)
            service_name: Service name for folder organization

        Returns:
            dict with sharepoint_item_id, sharepoint_url, sharepoint_web_url, stored_filename, file_size
        """
        try:
            # Generate unique filename
            file_ext = os.path.splitext(original_filename)[1].lower()
            unique_id = str(uuid.uuid4())
            stored_filename = f'{unique_id}{file_ext}'

            # New user-based folder structure: root/username/service/file
            # Username is the CLIENT for whom data is being uploaded
            safe_username = self._sanitize_folder_name(username) if username else self._sanitize_folder_name(client_name)
            safe_service = self._sanitize_folder_name(service_name) if service_name else category

            folder_path = f'{self.root_folder}/{safe_username}/{safe_service}'

            # Ensure folder exists
            self._ensure_folder_exists(folder_path)

            # Get file content
            if hasattr(file_stream, 'read'):
                file_stream.seek(0)
                file_content = file_stream.read()
            else:
                file_content = file_stream

            file_size = len(file_content)

            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            # For files smaller than 4MB, use simple upload
            if file_size < 4 * 1024 * 1024:
                upload_url = f'{drive_endpoint}/root:/{folder_path}/{stored_filename}:/content'

                headers['Content-Type'] = 'application/octet-stream'
                response = requests.put(upload_url, headers=headers, data=file_content)

                if response.status_code in [200, 201]:
                    result = response.json()
                    return {
                        'success': True,
                        'sharepoint_item_id': result.get('id'),
                        'sharepoint_url': result.get('@microsoft.graph.downloadUrl'),
                        'sharepoint_web_url': result.get('webUrl'),
                        'stored_filename': stored_filename,
                        'file_size': file_size,
                        'blob_name': f'{folder_path}/{stored_filename}'
                    }
                else:
                    current_app.logger.error(f'SharePoint upload failed: {response.text}')
                    return {
                        'success': False,
                        'error': f'Upload failed: {response.status_code} - {response.text}'
                    }
            else:
                # For larger files, use upload session
                return self._upload_large_file(file_content, folder_path, stored_filename)

        except Exception as e:
            current_app.logger.error(f'Error uploading to SharePoint: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def upload_raw_file(self, file_stream, file_path):
        """
        Upload a file directly to a specified path (for logos, etc.)

        Args:
            file_stream: File stream/bytes to upload
            file_path: Full path for the file in SharePoint

        Returns:
            dict with sharepoint_url, web_url
        """
        try:
            # Get folder path and filename
            if '/' in file_path:
                folder_path = '/'.join(file_path.split('/')[:-1])
                filename = file_path.split('/')[-1]
            else:
                folder_path = ''
                filename = file_path

            # Ensure folder exists if there is one
            if folder_path:
                self._ensure_folder_exists(folder_path)

            # Get file content
            if hasattr(file_stream, 'read'):
                file_stream.seek(0)
                file_content = file_stream.read()
            else:
                file_content = file_stream

            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            # Upload file
            if folder_path:
                upload_url = f'{drive_endpoint}/root:/{folder_path}/{filename}:/content'
            else:
                upload_url = f'{drive_endpoint}/root:/{filename}:/content'

            headers['Content-Type'] = 'application/octet-stream'
            response = requests.put(upload_url, headers=headers, data=file_content)

            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'sharepoint_url': result.get('@microsoft.graph.downloadUrl'),
                    'web_url': result.get('webUrl'),
                    'item_id': result.get('id')
                }
            else:
                current_app.logger.error(f'SharePoint raw upload failed: {response.text}')
                return {
                    'success': False,
                    'error': f'Upload failed: {response.status_code} - {response.text}'
                }

        except Exception as e:
            current_app.logger.error(f'Error uploading raw file to SharePoint: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _upload_large_file(self, file_content, folder_path, stored_filename):
        """Upload large files using upload session (for files > 4MB)"""
        try:
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'
            drive_endpoint = self._get_drive_endpoint()

            # Create upload session
            session_url = f'{drive_endpoint}/root:/{folder_path}/{stored_filename}:/createUploadSession'

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
                    'sharepoint_item_id': result.get('id'),
                    'sharepoint_url': result.get('@microsoft.graph.downloadUrl'),
                    'sharepoint_web_url': result.get('webUrl'),
                    'stored_filename': stored_filename,
                    'file_size': file_size,
                    'blob_name': f'{folder_path}/{stored_filename}'
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

    def get_download_url(self, item_id, expiry_hours=1):
        """
        Get a download URL for a file.

        Args:
            item_id: SharePoint item ID
            expiry_hours: Not used for SharePoint (Graph API provides temporary URLs)

        Returns:
            dict with download_url
        """
        try:
            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            url = f'{drive_endpoint}/items/{item_id}'
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

    def get_view_url(self, item_id, expiry_hours=24):
        """Get a view URL for a file (same as download for SharePoint)"""
        return self.get_download_url(item_id, expiry_hours)

    def create_sharing_link(self, item_id, link_type='view', scope='anonymous', expiry_hours=168):
        """
        Create a sharing link for a file.

        Args:
            item_id: SharePoint item ID
            link_type: 'view' or 'edit'
            scope: 'anonymous' or 'organization'
            expiry_hours: Link validity in hours (default 7 days)

        Returns:
            dict with sharing link URL
        """
        try:
            headers = self._get_headers()
            headers['Content-Type'] = 'application/json'
            drive_endpoint = self._get_drive_endpoint()

            url = f'{drive_endpoint}/items/{item_id}/createLink'

            link_data = {
                'type': link_type,
                'scope': scope
            }

            response = requests.post(url, headers=headers, json=link_data)

            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'link': result.get('link', {}).get('webUrl'),
                    'expires_in_hours': expiry_hours
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
        """Delete a file from SharePoint"""
        try:
            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            url = f'{drive_endpoint}/items/{item_id}'
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
        """Get file metadata from SharePoint"""
        try:
            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            url = f'{drive_endpoint}/items/{item_id}'
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

    def list_files_in_folder(self, folder_path, max_results=100):
        """List files in a SharePoint folder"""
        try:
            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            url = f'{drive_endpoint}/root:/{folder_path}:/children'
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                items = response.json().get('value', [])
                files = []
                for item in items[:max_results]:
                    files.append({
                        'id': item.get('id'),
                        'name': item.get('name'),
                        'size': item.get('size'),
                        'web_url': item.get('webUrl'),
                        'created': item.get('createdDateTime'),
                        'modified': item.get('lastModifiedDateTime'),
                        'is_folder': 'folder' in item
                    })
                return {
                    'success': True,
                    'files': files
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to list files: {response.status_code}'
                }

        except Exception as e:
            current_app.logger.error(f'Error listing files: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_client_folder_url(self, client_name, company_name=None, username=None):
        """
        Get the SharePoint web URL for a client's/user's folder.

        Args:
            client_name: Client name (legacy parameter)
            company_name: Company name for organized structure
            username: Username for organized structure

        Returns:
            dict with web_url and folder_id
        """
        try:
            headers = self._get_headers()
            drive_endpoint = self._get_drive_endpoint()

            if company_name and username:
                # New organized structure
                safe_company = self._sanitize_folder_name(company_name)
                safe_username = self._sanitize_folder_name(username)
                folder_path = f'{self.root_folder}/{safe_company}/{safe_username}'
            else:
                # Legacy structure
                safe_client_name = self._sanitize_folder_name(client_name)
                folder_path = f'{self.root_folder}/{safe_client_name}'

            url = f'{drive_endpoint}/root:/{folder_path}'
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return {
                    'success': True,
                    'web_url': response.json().get('webUrl'),
                    'folder_id': response.json().get('id')
                }
            else:
                return {
                    'success': False,
                    'error': f'Folder not found: {response.status_code}'
                }

        except Exception as e:
            current_app.logger.error(f'Error getting client folder URL: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
