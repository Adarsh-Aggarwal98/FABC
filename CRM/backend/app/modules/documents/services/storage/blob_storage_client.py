"""
Azure Blob Storage Client
=========================
Client for Azure Blob Storage document operations.
"""
import uuid
import os
from datetime import datetime, timedelta
from flask import current_app

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class BlobStorageClient:
    """Azure Blob Storage client for document operations"""

    def __init__(self):
        self.connection_string = current_app.config.get('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = current_app.config.get('AZURE_STORAGE_CONTAINER', 'crm-documents')
        self.account_name = current_app.config.get('AZURE_STORAGE_ACCOUNT_NAME')
        self.account_key = current_app.config.get('AZURE_STORAGE_ACCOUNT_KEY')

        if not AZURE_AVAILABLE:
            raise ImportError('azure-storage-blob package is not installed. Run: pip install azure-storage-blob')

    def _get_blob_service_client(self):
        """Get blob service client"""
        if not self.connection_string:
            raise ValueError('Azure Storage connection string not configured')
        return BlobServiceClient.from_connection_string(self.connection_string)

    def _ensure_container_exists(self):
        """Ensure the container exists, create if not"""
        try:
            blob_service_client = self._get_blob_service_client()
            container_client = blob_service_client.get_container_client(self.container_name)

            if not container_client.exists():
                container_client.create_container()
                current_app.logger.info(f'Created blob container: {self.container_name}')

            return container_client
        except Exception as e:
            current_app.logger.error(f'Error ensuring container exists: {str(e)}')
            raise

    def _sanitize_name(self, name):
        """
        Sanitize a name for use in blob paths.
        Removes or replaces invalid characters.
        """
        import re
        if not name:
            return 'Unknown'

        # Replace invalid characters with underscore
        # Azure blob paths don't allow: \ : * ? " < > |
        invalid_chars = r'[\\:\*\?"<>\|]'
        sanitized = re.sub(invalid_chars, '_', name)

        # Replace multiple spaces/underscores with single underscore
        sanitized = re.sub(r'[\s_]+', '_', sanitized)

        # Remove leading/trailing spaces and underscores
        sanitized = sanitized.strip(' _')

        # Limit length to 128 characters
        if len(sanitized) > 128:
            sanitized = sanitized[:128]

        return sanitized or 'Unknown'

    def _ensure_company_container_exists(self, company_name):
        """
        Ensure a container exists for the company, create if not.
        Container names must be lowercase and can only contain letters, numbers, and hyphens.
        """
        import re
        try:
            # Sanitize company name for container naming rules
            # Container names: 3-63 chars, lowercase, alphanumeric and hyphens, start with letter/number
            container_name = company_name.lower()
            container_name = re.sub(r'[^a-z0-9-]', '-', container_name)
            container_name = re.sub(r'-+', '-', container_name)  # Replace multiple hyphens
            container_name = container_name.strip('-')

            # Ensure minimum length
            if len(container_name) < 3:
                container_name = f'company-{container_name}'

            # Limit to max length
            if len(container_name) > 63:
                container_name = container_name[:63].rstrip('-')

            blob_service_client = self._get_blob_service_client()
            container_client = blob_service_client.get_container_client(container_name)

            if not container_client.exists():
                container_client.create_container()
                current_app.logger.info(f'Created blob container: {container_name}')

            return container_client, container_name

        except Exception as e:
            current_app.logger.error(f'Error ensuring company container exists: {str(e)}')
            raise

    def upload_file(self, file_stream, original_filename, service_request_id=None, category='supporting_document',
                    company_name=None, username=None, service_name=None):
        """
        Upload a file to Azure Blob Storage with organized folder structure.

        Folder structure: {company_container}/{username}/{service_name}/{filename}
        If company_name is provided, uses company-specific container.
        Otherwise falls back to default container with legacy structure.

        Args:
            file_stream: File stream/bytes to upload
            original_filename: Original filename
            service_request_id: Optional service request ID for organizing (legacy)
            category: Document category for organizing (legacy fallback)
            company_name: Company name for container organization
            username: Username for folder organization
            service_name: Service name for folder organization

        Returns:
            dict with blob_name, blob_url, stored_filename, file_size
        """
        try:
            # Generate unique filename
            file_ext = os.path.splitext(original_filename)[1].lower()
            unique_id = str(uuid.uuid4())
            stored_filename = f'{unique_id}{file_ext}'

            # Get file content
            if hasattr(file_stream, 'read'):
                file_stream.seek(0)
                file_content = file_stream.read()
            else:
                file_content = file_stream

            file_size = len(file_content)

            # Determine container and blob path based on available info
            if company_name:
                # New organized structure: company container / username / service_name / file
                container_client, container_name = self._ensure_company_container_exists(company_name)

                # Build organized path
                safe_username = self._sanitize_name(username) if username else 'Unknown_User'
                safe_service = self._sanitize_name(service_name) if service_name else category

                blob_name = f'{safe_username}/{safe_service}/{stored_filename}'
            else:
                # Legacy structure for backward compatibility
                container_client = self._ensure_container_exists()
                container_name = self.container_name

                if service_request_id:
                    blob_name = f'requests/{service_request_id}/{category}/{stored_filename}'
                else:
                    blob_name = f'general/{category}/{stored_filename}'

            # Upload blob
            blob_client = container_client.get_blob_client(blob_name)

            # Set content type based on file extension
            content_type = self._get_content_type(file_ext)

            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )

            # Get the blob URL
            blob_url = blob_client.url

            return {
                'success': True,
                'blob_name': blob_name,
                'blob_url': blob_url,
                'stored_filename': stored_filename,
                'file_size': file_size,
                'container_name': container_name
            }

        except Exception as e:
            current_app.logger.error(f'Error uploading to Blob Storage: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def upload_raw_file(self, file_stream, blob_name, public_url=False):
        """
        Upload a file directly to a specified blob path (for logos, etc.)

        Args:
            file_stream: File stream/bytes to upload
            blob_name: Full path/name for the blob
            public_url: If True, returns a SAS-signed URL with long expiry (for logos)

        Returns:
            dict with blob_name, blob_url
        """
        try:
            # Get file content
            if hasattr(file_stream, 'read'):
                file_stream.seek(0)
                file_content = file_stream.read()
            else:
                file_content = file_stream

            # Get file extension for content type
            file_ext = os.path.splitext(blob_name)[1].lower() if '.' in blob_name else ''

            # Ensure container exists
            container_client = self._ensure_container_exists()

            # Upload blob
            blob_client = container_client.get_blob_client(blob_name)
            content_type = self._get_content_type(file_ext)

            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )

            # Generate URL - use SAS token for public access if requested
            if public_url and self.account_name and self.account_key:
                # Generate SAS token with 1 year expiry for logos
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=self.container_name,
                    blob_name=blob_name,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(days=365)
                )
                blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            else:
                blob_url = blob_client.url

            return {
                'success': True,
                'blob_name': blob_name,
                'blob_url': blob_url
            }

        except Exception as e:
            current_app.logger.error(f'Error uploading raw file to Blob Storage: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _get_content_type(self, file_ext):
        """Get content type from file extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.csv': 'text/csv',
            '.txt': 'text/plain',
        }
        return content_types.get(file_ext.lower(), 'application/octet-stream')

    def get_download_url(self, blob_name, expiry_hours=1):
        """
        Get a SAS URL for downloading a blob

        Args:
            blob_name: Name/path of the blob
            expiry_hours: How many hours the URL should be valid

        Returns:
            dict with download_url
        """
        try:
            if not self.account_name or not self.account_key:
                # If no account key, return the direct URL (requires public access)
                blob_service_client = self._get_blob_service_client()
                container_client = blob_service_client.get_container_client(self.container_name)
                blob_client = container_client.get_blob_client(blob_name)
                return {
                    'success': True,
                    'download_url': blob_client.url
                }

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )

            # Construct URL with SAS token
            blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"

            return {
                'success': True,
                'download_url': blob_url
            }

        except Exception as e:
            current_app.logger.error(f'Error generating download URL: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_view_url(self, blob_name, expiry_hours=24):
        """
        Get a SAS URL for viewing a blob in browser (longer expiry for viewing)

        Args:
            blob_name: Name/path of the blob
            expiry_hours: How many hours the URL should be valid

        Returns:
            dict with view_url
        """
        return self.get_download_url(blob_name, expiry_hours)

    def delete_file(self, blob_name):
        """Delete a blob from storage"""
        try:
            blob_service_client = self._get_blob_service_client()
            container_client = blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            blob_client.delete_blob()

            return {'success': True}

        except Exception as e:
            current_app.logger.error(f'Error deleting blob: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def get_blob_properties(self, blob_name):
        """Get blob properties/metadata"""
        try:
            blob_service_client = self._get_blob_service_client()
            container_client = blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            properties = blob_client.get_blob_properties()

            return {
                'success': True,
                'properties': {
                    'size': properties.size,
                    'content_type': properties.content_settings.content_type,
                    'created_on': properties.creation_time.isoformat() if properties.creation_time else None,
                    'last_modified': properties.last_modified.isoformat() if properties.last_modified else None,
                    'etag': properties.etag
                }
            }

        except Exception as e:
            current_app.logger.error(f'Error getting blob properties: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def copy_blob(self, source_blob_name, dest_blob_name):
        """Copy a blob to a new location"""
        try:
            blob_service_client = self._get_blob_service_client()
            container_client = blob_service_client.get_container_client(self.container_name)

            source_blob = container_client.get_blob_client(source_blob_name)
            dest_blob = container_client.get_blob_client(dest_blob_name)

            # Get source URL with SAS for copy operation
            source_url_result = self.get_download_url(source_blob_name, expiry_hours=1)
            if not source_url_result.get('success'):
                return source_url_result

            dest_blob.start_copy_from_url(source_url_result['download_url'])

            return {
                'success': True,
                'dest_blob_name': dest_blob_name
            }

        except Exception as e:
            current_app.logger.error(f'Error copying blob: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def list_blobs(self, prefix=None, max_results=100):
        """List blobs in the container"""
        try:
            blob_service_client = self._get_blob_service_client()
            container_client = blob_service_client.get_container_client(self.container_name)

            blobs = []
            blob_list = container_client.list_blobs(name_starts_with=prefix)

            for blob in blob_list:
                blobs.append({
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified.isoformat() if blob.last_modified else None
                })
                if len(blobs) >= max_results:
                    break

            return {
                'success': True,
                'blobs': blobs
            }

        except Exception as e:
            current_app.logger.error(f'Error listing blobs: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
