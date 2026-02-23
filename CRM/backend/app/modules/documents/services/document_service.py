"""
Document Service - Storage Abstraction Layer
=============================================

This module provides a unified interface for document storage operations,
abstracting away the underlying storage provider (Google Drive, SharePoint,
Azure Blob, Zoho Drive, or local filesystem).

Storage Selection Priority:
--------------------------
1. Company-specific storage config (if enabled)
2. System-level Google Drive (if configured)
3. System-level SharePoint (if enabled)
4. Google Apps Script Web App (simpler OAuth alternative)
5. Azure Blob Storage (if configured)
6. Local filesystem (fallback)

Key Operations:
--------------
- upload_document(): Upload file with metadata to storage
- get_download_url(): Get temporary download URL
- get_view_url(): Get longer-lived URL for browser viewing
- delete_document(): Soft delete (DB) + storage deletion
- create_sharing_link(): Create shareable link for external access

Folder Organization:
------------------
Documents are organized by: {company_name}/{username}/{service_name}/
This allows easy browsing in cloud storage providers.

Author: CRM Development Team
"""

import os
import uuid
import logging
import mimetypes
from flask import current_app
from app.extensions import db
from app.modules.documents.models.document import Document
from app.modules.documents.repositories.document_repository import DocumentRepository
from app.modules.services.models import ServiceRequest
from app.modules.user.models import User

# Configure module-level logger
logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service for document operations with multiple storage backends.

    Supported backends:
    - Google Drive (OAuth)
    - Google Apps Script (simpler alternative)
    - SharePoint / OneDrive
    - Azure Blob Storage
    - Zoho Drive
    - Local filesystem (fallback)

    Usage:
        # Upload a document
        result = DocumentService.upload_document(file, user_id, request_id)

        # Get download URL
        result = DocumentService.get_download_url(document_id)

        # Delete document
        result = DocumentService.delete_document(document_id, user_id, is_admin)
    """

    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'gif'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def _allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in DocumentService.ALLOWED_EXTENSIONS

    @staticmethod
    def _get_file_type(filename):
        """Get file type from filename"""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return 'unknown'

    @staticmethod
    def _get_mime_type(filename):
        """Get MIME type from filename"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    @staticmethod
    def _get_storage_client(company_id=None):
        """
        Get the appropriate storage client based on configuration.
        Priority: SharePoint (default) > Company Storage Config > Google Drive > Azure Blob > Local

        Args:
            company_id: Optional company ID to check company-specific storage config
        """
        # Check for SharePoint FIRST (system-level) - DEFAULT STORAGE
        # SharePoint is the primary storage provider using Microsoft Graph API
        graph_client_id = current_app.config.get('GRAPH_CLIENT_ID')
        graph_client_secret = current_app.config.get('GRAPH_CLIENT_SECRET')
        graph_tenant_id = current_app.config.get('GRAPH_TENANT_ID')
        site_id = current_app.config.get('SHAREPOINT_SITE_ID')
        drive_id = current_app.config.get('SHAREPOINT_DRIVE_ID')

        if graph_client_id and graph_client_secret and graph_tenant_id and (site_id or drive_id):
            from app.modules.documents.services.storage.sharepoint_client import SharePointClient
            logger.info('[Storage] Using SharePoint as default storage (Graph API configured)')
            return SharePointClient(), 'sharepoint'

        # Check company-specific storage configuration
        if company_id:
            from app.modules.company.models import CompanyStorageConfig, StorageProviderType
            company_config = CompanyStorageConfig.query.filter_by(
                company_id=company_id,
                is_enabled=True
            ).first()

            if company_config:
                if company_config.provider == StorageProviderType.SHAREPOINT:
                    if company_config.sharepoint_site_id or company_config.sharepoint_drive_id:
                        from app.modules.documents.services.storage.sharepoint_client import SharePointClient
                        return SharePointClient(), 'sharepoint'

                elif company_config.provider == StorageProviderType.GOOGLE_DRIVE:
                    if company_config.google_access_token or company_config.google_refresh_token:
                        from app.modules.documents.services.storage.google_drive_client import GoogleDriveClient
                        client = GoogleDriveClient(company_config)
                        if client.is_configured():
                            return client, 'google_drive'

                elif company_config.provider == StorageProviderType.ZOHO_DRIVE:
                    if company_config.zoho_access_token or company_config.zoho_refresh_token:
                        from app.modules.documents.services.storage.zoho_drive_client import ZohoDriveClient
                        client = ZohoDriveClient(company_config)
                        if client.is_configured():
                            return client, 'zoho_drive'

        # Check for system-level Google Drive configuration
        google_client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
        google_client_secret = current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET')
        if google_client_id and google_client_secret:
            from app.modules.documents.services.storage.google_drive_client import GoogleDriveClient
            config = {
                'google_client_id': google_client_id,
                'google_client_secret': google_client_secret,
                'google_access_token': current_app.config.get('GOOGLE_DRIVE_ACCESS_TOKEN'),
                'google_refresh_token': current_app.config.get('GOOGLE_DRIVE_REFRESH_TOKEN'),
                'google_root_folder_id': current_app.config.get('GOOGLE_DRIVE_ROOT_FOLDER_ID'),
            }
            client = GoogleDriveClient(config)
            if client.is_configured():
                return client, 'google_drive'

        # Check for Google Apps Script Web App (simpler than OAuth)
        apps_script_url = current_app.config.get('GOOGLE_APPS_SCRIPT_URL')
        if apps_script_url:
            from app.modules.documents.services.storage.google_apps_script_client import GoogleAppsScriptClient
            client = GoogleAppsScriptClient(
                web_app_url=apps_script_url,
                root_folder_id=current_app.config.get('GOOGLE_APPS_SCRIPT_FOLDER_ID')
            )
            if client.is_configured():
                return client, 'google_apps_script'

        # Fallback to Azure Blob Storage
        connection_string = current_app.config.get('AZURE_STORAGE_CONNECTION_STRING')
        if connection_string:
            from app.modules.documents.services.storage.blob_storage_client import BlobStorageClient
            return BlobStorageClient(), 'blob'

        return None, 'local'

    @staticmethod
    def _get_client_name(user_id, service_request_id=None):
        """
        Get the client name for folder organization.
        Uses the user associated with the service request, or the uploading user.
        """
        client_name = None

        # If there's a service request, get the client name from the request owner
        if service_request_id:
            service_request = ServiceRequest.query.get(service_request_id)
            if service_request and service_request.user:
                user = service_request.user
                client_name = user.full_name or user.email

        # Fallback to the uploading user's name
        if not client_name:
            user = User.query.get(user_id)
            if user:
                client_name = user.full_name or user.email

        return client_name or 'Unknown_Client'

    @staticmethod
    def _get_folder_organization_info(user_id, service_request_id=None):
        """
        Get the folder organization info for document storage.
        Returns username (client name) and service_name for organized storage.

        Folder structure: {username}/{service_name}/

        When admin/accountant uploads for a user, folder is named after that user (client),
        NOT the company. This allows easy browsing by client name in SharePoint.

        Args:
            user_id: ID of user uploading the document
            service_request_id: Optional service request ID

        Returns:
            dict with company_name (None), username (client name), service_name
        """
        username = None
        service_name = None

        # If there's a service request, get info from the REQUEST OWNER (client)
        # This ensures folder is named after the client, not the uploader
        if service_request_id:
            service_request = ServiceRequest.query.get(service_request_id)
            if service_request:
                # Get service name from the request
                if service_request.service:
                    service_name = service_request.service.name

                # Get username from the request owner (THE CLIENT for whom data is uploaded)
                if service_request.user:
                    client_user = service_request.user
                    username = client_user.full_name or client_user.email

        # Fallback to uploading user's info only if no service request
        if not username:
            user = User.query.get(user_id)
            if user:
                username = user.full_name or user.email

        return {
            'company_name': None,  # Not using company-based organization
            'username': username or 'Unknown_User',
            'service_name': service_name
        }

    @staticmethod
    def upload_to_storage(file, filename):
        """
        Upload a file to storage and return the URL.
        Used for simple uploads like company logos.

        Args:
            file: FileStorage object from Flask request
            filename: Target filename/path in storage

        Returns:
            str: URL of the uploaded file
        """
        storage_client, storage_type = DocumentService._get_storage_client()

        if storage_type == 'sharepoint':
            # Upload to SharePoint
            file.seek(0)
            result = storage_client.upload_raw_file(file, filename)
            if result.get('success'):
                return result.get('sharepoint_url') or result.get('web_url', '')
            raise Exception(result.get('error', 'SharePoint upload failed'))

        elif storage_client and storage_type == 'blob':
            # Upload to Azure Blob Storage
            file.seek(0)
            result = storage_client.upload_raw_file(file, filename)
            if result.get('success'):
                return result.get('blob_url', '')
            raise Exception(result.get('error', 'Blob storage upload failed'))

        else:
            # Fallback to local storage
            import os
            upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            file_path = os.path.join(upload_dir, filename)

            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            file.seek(0)
            file.save(file_path)

            # Return a relative URL for local files
            return f'/uploads/{filename}'

    @staticmethod
    def upload_document(file, user_id, service_request_id=None, category='supporting_document', description=None):
        """
        Upload a document to the configured storage backend and store metadata in database.

        Folder structure varies by provider but follows the pattern:
        {company_name}/{username}/{service_name}/{category}/

        Args:
            file: FileStorage object from Flask request
            user_id: ID of user uploading the document
            service_request_id: Optional service request to link document to
            category: Document category (supporting_document, id_proof, etc.)
            description: Optional description

        Returns:
            dict: {'success': True, 'document': {...}} on success
                  {'success': False, 'error': '...'} on failure
        """
        logger.info(f"DocumentService.upload_document: Starting upload for user_id={user_id}, request_id={service_request_id}")

        try:
            # Step 1: Validate file
            if not file or not file.filename:
                logger.warning("Upload failed: No file provided")
                return {'success': False, 'error': 'No file provided'}

            original_filename = file.filename

            if not DocumentService._allowed_file(original_filename):
                return {
                    'success': False,
                    'error': f'File type not allowed. Allowed types: {", ".join(DocumentService.ALLOWED_EXTENSIONS)}'
                }

            # Validate service request if provided
            if service_request_id:
                request = ServiceRequest.query.get(service_request_id)
                if not request:
                    return {'success': False, 'error': 'Service request not found'}

            # Get file info
            file_type = DocumentService._get_file_type(original_filename)
            mime_type = DocumentService._get_mime_type(original_filename)

            # Get client name for folder organization (legacy)
            client_name = DocumentService._get_client_name(user_id, service_request_id)

            # Get organized folder info (new structure)
            folder_info = DocumentService._get_folder_organization_info(user_id, service_request_id)
            company_name = folder_info['company_name']
            username = folder_info['username']
            service_name = folder_info['service_name']

            # Get storage client
            # Get company_id from the user associated with service request
            company_id = None
            if service_request_id:
                request = ServiceRequest.query.get(service_request_id)
                if request and request.user:
                    company_id = request.user.company_id
            elif user_id:
                user = User.query.get(user_id)
                if user:
                    company_id = user.company_id

            storage_client, storage_type = DocumentService._get_storage_client(company_id)

            if storage_type == 'google_drive':
                # Upload to Google Drive with organized folder structure
                result = storage_client.upload_file(
                    file_stream=file,
                    original_filename=original_filename,
                    client_name=client_name,
                    category=category,
                    service_request_id=service_request_id,
                    company_name=company_name,
                    username=username,
                    service_name=service_name
                )

                if not result.get('success'):
                    return {
                        'success': False,
                        'error': result.get('error', 'Google Drive upload failed')
                    }

                # Create document record with Google Drive fields
                document = Document(
                    original_filename=original_filename,
                    stored_filename=result.get('file_name', original_filename),
                    file_type=file_type,
                    file_size=int(result.get('size', 0)) if result.get('size') else 0,
                    mime_type=result.get('mime_type', mime_type),
                    storage_path=result['file_id'],  # Google Drive file ID
                    storage_url=result.get('web_view_link', ''),
                    storage_type='google_drive',
                    external_item_id=result['file_id'],
                    external_web_url=result.get('web_view_link', ''),
                    client_folder_name=client_name,
                    company_id=company_id,
                    uploaded_by_id=user_id,
                    service_request_id=service_request_id,
                    document_category=category,
                    description=description
                )

            elif storage_type == 'zoho_drive':
                # Upload to Zoho Drive with organized folder structure
                result = storage_client.upload_file(
                    file_stream=file,
                    original_filename=original_filename,
                    client_name=client_name,
                    category=category,
                    service_request_id=service_request_id,
                    company_name=company_name,
                    username=username,
                    service_name=service_name
                )

                if not result.get('success'):
                    return {
                        'success': False,
                        'error': result.get('error', 'Zoho Drive upload failed')
                    }

                # Create document record with Zoho Drive fields
                document = Document(
                    original_filename=original_filename,
                    stored_filename=result.get('file_name', original_filename),
                    file_type=file_type,
                    file_size=int(result.get('size', 0)) if result.get('size') else 0,
                    mime_type=mime_type,
                    storage_path=result['file_id'],  # Zoho file ID
                    storage_url=result.get('permalink', ''),
                    storage_type='zoho_drive',
                    external_item_id=result['file_id'],
                    external_web_url=result.get('permalink', ''),
                    client_folder_name=client_name,
                    company_id=company_id,
                    uploaded_by_id=user_id,
                    service_request_id=service_request_id,
                    document_category=category,
                    description=description
                )

            elif storage_type == 'sharepoint':
                # Upload to SharePoint with organized folder structure
                result = storage_client.upload_file(
                    file_stream=file,
                    original_filename=original_filename,
                    client_name=client_name,
                    category=category,
                    service_request_id=service_request_id,
                    company_name=company_name,
                    username=username,
                    service_name=service_name
                )

                if not result.get('success'):
                    return {
                        'success': False,
                        'error': result.get('error', 'SharePoint upload failed')
                    }

                # Create anonymous sharing link (like Azure SAS URL) for direct access
                public_url = result.get('sharepoint_web_url', '')
                item_id = result.get('sharepoint_item_id')
                if item_id:
                    try:
                        sharing_result = storage_client.create_sharing_link(
                            item_id, link_type='view', scope='anonymous'
                        )
                        if sharing_result.get('success') and sharing_result.get('link'):
                            public_url = sharing_result['link']
                            logger.info(f'Created anonymous sharing link for document')
                    except Exception as share_err:
                        logger.warning(f'Could not create sharing link, using web URL: {share_err}')

                # Create document record with SharePoint fields
                document = Document(
                    original_filename=original_filename,
                    stored_filename=result['stored_filename'],
                    file_type=file_type,
                    file_size=result['file_size'],
                    mime_type=mime_type,
                    storage_path=result['blob_name'],  # SharePoint folder path
                    storage_url=result.get('sharepoint_url', ''),
                    storage_type='sharepoint',
                    external_item_id=result['sharepoint_item_id'],
                    external_web_url=public_url,
                    client_folder_name=client_name,
                    company_id=company_id,
                    uploaded_by_id=user_id,
                    service_request_id=service_request_id,
                    document_category=category,
                    description=description
                )

            elif storage_type == 'google_apps_script':
                # Upload to Google Drive via Apps Script Web App
                result = storage_client.upload_file(
                    file_stream=file,
                    original_filename=original_filename,
                    client_name=client_name,
                    category=category,
                    service_request_id=service_request_id,
                    company_name=company_name,
                    username=username,
                    service_name=service_name
                )

                if not result.get('success'):
                    return {
                        'success': False,
                        'error': result.get('error', 'Google Apps Script upload failed')
                    }

                # Create document record with Google Drive fields
                document = Document(
                    original_filename=original_filename,
                    stored_filename=result.get('file_name', original_filename),
                    file_type=file_type,
                    file_size=int(result.get('size', 0)) if result.get('size') else 0,
                    mime_type=result.get('mime_type', mime_type),
                    storage_path=result['file_id'],  # Google Drive file ID
                    storage_url=result.get('web_view_link', ''),
                    storage_type='google_apps_script',
                    external_item_id=result['file_id'],
                    external_web_url=result.get('web_view_link', ''),
                    client_folder_name=client_name,
                    company_id=company_id,
                    uploaded_by_id=user_id,
                    service_request_id=service_request_id,
                    document_category=category,
                    description=description
                )

            elif storage_client:
                # Upload to Azure Blob Storage with organized folder structure
                result = storage_client.upload_file(
                    file_stream=file,
                    original_filename=original_filename,
                    service_request_id=service_request_id,
                    category=category,
                    company_name=company_name,
                    username=username,
                    service_name=service_name
                )

                if not result.get('success'):
                    return {
                        'success': False,
                        'error': result.get('error', 'Blob storage upload failed')
                    }

                # Create document record
                document = Document(
                    original_filename=original_filename,
                    stored_filename=result['stored_filename'],
                    file_type=file_type,
                    file_size=result['file_size'],
                    mime_type=mime_type,
                    storage_path=result['blob_name'],  # Azure blob path
                    storage_url=result['blob_url'],
                    storage_type='blob',
                    client_folder_name=client_name,
                    company_id=company_id,
                    uploaded_by_id=user_id,
                    service_request_id=service_request_id,
                    document_category=category,
                    description=description
                )
            else:
                # Fallback to local storage if no cloud storage configured
                unique_id = str(uuid.uuid4())
                file_ext = os.path.splitext(original_filename)[1].lower()
                stored_filename = f'{unique_id}{file_ext}'

                # Create uploads directory structure
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                if service_request_id:
                    upload_path = os.path.join(upload_dir, 'requests', service_request_id, category)
                else:
                    upload_path = os.path.join(upload_dir, 'general', category)

                os.makedirs(upload_path, exist_ok=True)

                # Save file locally
                file_path = os.path.join(upload_path, stored_filename)
                file.seek(0)
                file.save(file_path)

                file_size = os.path.getsize(file_path)

                # Build blob name for local storage (same structure)
                if service_request_id:
                    blob_name = f'requests/{service_request_id}/{category}/{stored_filename}'
                else:
                    blob_name = f'general/{category}/{stored_filename}'

                # Create document record with local path
                document = Document(
                    original_filename=original_filename,
                    stored_filename=stored_filename,
                    file_type=file_type,
                    file_size=file_size,
                    mime_type=mime_type,
                    storage_path=blob_name,  # Local file path
                    storage_url=f'/api/documents/{stored_filename}/download',
                    storage_type='local',
                    client_folder_name=client_name,
                    company_id=company_id,
                    uploaded_by_id=user_id,
                    service_request_id=service_request_id,
                    document_category=category,
                    description=description
                )

            DocumentRepository.create(document)

            return {
                'success': True,
                'document': document.to_dict()
            }

        except Exception as e:
            DocumentRepository.rollback()
            current_app.logger.error(f'Error uploading document: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_document(document_id):
        """Get a document by ID"""
        return DocumentRepository.get_active_by_id(document_id)

    @staticmethod
    def get_documents_for_request(service_request_id):
        """Get all documents for a service request"""
        documents = DocumentRepository.get_for_service_request(service_request_id)
        return [doc.to_dict() for doc in documents]

    @staticmethod
    def get_documents_for_user(user_id, limit=50):
        """Get documents uploaded by a user"""
        documents = DocumentRepository.get_for_user(user_id, limit)
        return [doc.to_dict() for doc in documents]

    @staticmethod
    def get_download_url(document_id):
        """Get a download URL for a document"""
        document = DocumentRepository.get_by_id(document_id)
        if not document or not document.is_active:
            return {'success': False, 'error': 'Document not found'}

        # Get storage path with fallback to legacy column
        storage_path = document.storage_path or document.blob_name
        external_id = document.external_item_id or getattr(document, 'sharepoint_item_id', None)

        # Get company_id for storage client selection
        company_id = document.company_id

        if document.storage_type == 'google_drive' and storage_path:
            # Get download URL from Google Drive
            storage_client, storage_type = DocumentService._get_storage_client(company_id)
            if storage_client and storage_type == 'google_drive':
                result = storage_client.get_download_url(storage_path)
                if result.get('success'):
                    return {
                        'success': True,
                        'download_url': result.get('download_url'),
                        'filename': document.original_filename,
                        'web_url': result.get('web_view_link')
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'Google Drive storage not configured'
                }

        elif document.storage_type == 'google_apps_script' and storage_path:
            # Get download URL from Google Apps Script
            from app.modules.documents.services.storage.google_apps_script_client import GoogleAppsScriptClient
            apps_script_url = current_app.config.get('GOOGLE_APPS_SCRIPT_URL')
            if apps_script_url:
                client = GoogleAppsScriptClient(web_app_url=apps_script_url)
                result = client.get_download_url(storage_path)
                if result.get('success'):
                    return {
                        'success': True,
                        'download_url': result.get('download_url'),
                        'filename': document.original_filename,
                        'web_url': result.get('web_view_link')
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'Google Apps Script not configured'
                }

        elif document.storage_type == 'zoho_drive' and storage_path:
            # Get download URL from Zoho Drive
            storage_client, storage_type = DocumentService._get_storage_client(company_id)
            if storage_client and storage_type == 'zoho_drive':
                result = storage_client.get_download_url(storage_path)
                if result.get('success'):
                    return {
                        'success': True,
                        'download_url': result.get('download_url'),
                        'filename': document.original_filename
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'Zoho Drive storage not configured'
                }

        elif document.storage_type == 'sharepoint' and external_id:
            # Get fresh download URL from SharePoint
            storage_client, _ = DocumentService._get_storage_client(company_id)
            if storage_client and hasattr(storage_client, 'get_download_url'):
                result = storage_client.get_download_url(external_id)
                if result.get('success'):
                    return {
                        'success': True,
                        'download_url': result['download_url'],
                        'filename': document.original_filename,
                        'web_url': result.get('web_url')
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'SharePoint storage not configured'
                }

        elif document.storage_type == 'blob' and storage_path:
            # Get fresh SAS URL from blob storage
            storage_client, storage_type = DocumentService._get_storage_client(company_id)
            if storage_client and storage_type == 'blob':
                result = storage_client.get_download_url(storage_path, expiry_hours=1)
                if result.get('success'):
                    return {
                        'success': True,
                        'download_url': result['download_url'],
                        'filename': document.original_filename
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'Blob storage not configured'
                }
        else:
            # Local storage - return the stored URL
            storage_url = document.storage_url or document.blob_url
            return {
                'success': True,
                'download_url': storage_url,
                'filename': document.original_filename
            }

    @staticmethod
    def get_view_url(document_id):
        """Get a view URL for a document (longer expiry for viewing in browser)"""
        document = DocumentRepository.get_by_id(document_id)
        if not document or not document.is_active:
            return {'success': False, 'error': 'Document not found'}

        sharepoint_id = document.external_item_id or getattr(document, 'sharepoint_item_id', None)
        if document.storage_type == 'sharepoint' and sharepoint_id:
            # Get view URL from SharePoint
            storage_client, _ = DocumentService._get_storage_client()
            if storage_client and hasattr(storage_client, 'get_view_url'):
                result = storage_client.get_view_url(sharepoint_id)
                if result.get('success'):
                    return {
                        'success': True,
                        'view_url': result['download_url'],
                        'filename': document.original_filename,
                        'mime_type': document.mime_type,
                        'web_url': result.get('web_url')
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'SharePoint storage not configured'
                }

        elif document.storage_type == 'blob' and document.blob_name:
            storage_client, storage_type = DocumentService._get_storage_client()
            if storage_client and storage_type == 'blob':
                result = storage_client.get_view_url(document.blob_name, expiry_hours=24)
                if result.get('success'):
                    return {
                        'success': True,
                        'view_url': result['download_url'],
                        'filename': document.original_filename,
                        'mime_type': document.mime_type
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'Blob storage not configured'
                }
        else:
            return {
                'success': True,
                'view_url': document.blob_url,
                'filename': document.original_filename,
                'mime_type': document.mime_type
            }

    @staticmethod
    def delete_document(document_id, user_id, is_admin=False):
        """
        Delete a document

        Args:
            document_id: ID of document to delete
            user_id: ID of user requesting deletion
            is_admin: Whether user is admin (can delete any document)
        """
        document = DocumentRepository.get_by_id(document_id)
        if not document:
            return {'success': False, 'error': 'Document not found'}

        # Check permission
        if not is_admin and document.uploaded_by_id != user_id:
            return {'success': False, 'error': 'Permission denied'}

        try:
            if document.storage_type == 'google_drive' and document.blob_name:
                # Delete from Google Drive
                storage_client, storage_type = DocumentService._get_storage_client()
                if storage_client and storage_type == 'google_drive':
                    result = storage_client.delete_file(document.blob_name)
                    if not result.get('success'):
                        current_app.logger.warning(f'Failed to delete from Google Drive: {result.get("error")}')

            elif document.storage_type == 'zoho_drive' and document.blob_name:
                # Delete from Zoho Drive
                storage_client, storage_type = DocumentService._get_storage_client()
                if storage_client and storage_type == 'zoho_drive':
                    result = storage_client.delete_file(document.blob_name)
                    if not result.get('success'):
                        current_app.logger.warning(f'Failed to delete from Zoho Drive: {result.get("error")}')

            elif document.storage_type == 'google_apps_script' and document.storage_path:
                # Delete from Google Drive via Apps Script
                from app.modules.documents.services.storage.google_apps_script_client import GoogleAppsScriptClient
                apps_script_url = current_app.config.get('GOOGLE_APPS_SCRIPT_URL')
                if apps_script_url:
                    client = GoogleAppsScriptClient(web_app_url=apps_script_url)
                    result = client.delete_file(document.storage_path)
                    if not result.get('success'):
                        current_app.logger.warning(f'Failed to delete from Google Apps Script: {result.get("error")}')

            elif document.storage_type == 'sharepoint' and document.sharepoint_item_id:
                # Delete from SharePoint
                storage_client, _ = DocumentService._get_storage_client()
                if storage_client and hasattr(storage_client, 'delete_file'):
                    result = storage_client.delete_file(document.sharepoint_item_id)
                    if not result.get('success'):
                        current_app.logger.warning(f'Failed to delete from SharePoint: {result.get("error")}')

            elif document.storage_type == 'blob' and document.blob_name:
                # Delete from Azure Blob Storage
                storage_client, storage_type = DocumentService._get_storage_client()
                if storage_client and storage_type == 'blob':
                    result = storage_client.delete_file(document.blob_name)
                    if not result.get('success'):
                        current_app.logger.warning(f'Failed to delete from blob storage: {result.get("error")}')
            else:
                # Delete local file
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                if document.service_request_id:
                    file_path = os.path.join(
                        upload_dir, 'requests', document.service_request_id,
                        document.document_category or 'other', document.stored_filename
                    )
                else:
                    file_path = os.path.join(
                        upload_dir, 'general',
                        document.document_category or 'other', document.stored_filename
                    )

                if os.path.exists(file_path):
                    os.remove(file_path)

            # Soft delete - mark as inactive
            DocumentRepository.soft_delete(document)

            return {'success': True}

        except Exception as e:
            DocumentRepository.rollback()
            current_app.logger.error(f'Error deleting document: {str(e)}')
            return {'success': False, 'error': str(e)}

    @staticmethod
    def create_sharing_link(document_id, expiry_hours=168):
        """
        Create a sharing link for a document (valid for 7 days by default)

        Args:
            document_id: ID of the document
            expiry_hours: How long the link should be valid (default 7 days)
        """
        document = DocumentRepository.get_by_id(document_id)
        if not document or not document.is_active:
            return {'success': False, 'error': 'Document not found'}

        if document.storage_type == 'sharepoint' and document.sharepoint_item_id:
            # Create sharing link via SharePoint
            storage_client, _ = DocumentService._get_storage_client()
            if storage_client and hasattr(storage_client, 'create_sharing_link'):
                result = storage_client.create_sharing_link(
                    document.sharepoint_item_id,
                    link_type='view',
                    scope='anonymous',
                    expiry_hours=expiry_hours
                )
                if result.get('success'):
                    return {
                        'success': True,
                        'link': result['link'],
                        'expires_in_hours': expiry_hours
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'SharePoint storage not configured'
                }

        elif document.storage_type == 'blob' and document.blob_name:
            storage_client, storage_type = DocumentService._get_storage_client()
            if storage_client and storage_type == 'blob':
                result = storage_client.get_download_url(document.blob_name, expiry_hours=expiry_hours)
                if result.get('success'):
                    return {
                        'success': True,
                        'link': result['download_url'],
                        'expires_in_hours': expiry_hours
                    }
                return result
            else:
                return {
                    'success': False,
                    'error': 'Blob storage not configured'
                }
        else:
            return {
                'success': False,
                'error': 'Sharing links only available for cloud storage documents'
            }

    @staticmethod
    def get_client_folder_url(client_name):
        """
        Get the SharePoint web URL for a client's document folder.
        Only works when SharePoint storage is enabled.

        Args:
            client_name: Name of the client

        Returns:
            dict with web_url for the client's folder
        """
        storage_client, storage_type = DocumentService._get_storage_client()

        if storage_type != 'sharepoint':
            return {
                'success': False,
                'error': 'SharePoint storage not enabled'
            }

        if hasattr(storage_client, 'get_client_folder_url'):
            return storage_client.get_client_folder_url(client_name)

        return {
            'success': False,
            'error': 'Method not available'
        }

    @staticmethod
    def get_documents_by_client(client_name, limit=100):
        """
        Get all documents for a specific client (by client folder name).

        Args:
            client_name: The client name used for folder organization
            limit: Maximum number of documents to return

        Returns:
            list of document dictionaries
        """
        documents = DocumentRepository.get_by_client_folder(client_name, limit)
        return [doc.to_dict() for doc in documents]
