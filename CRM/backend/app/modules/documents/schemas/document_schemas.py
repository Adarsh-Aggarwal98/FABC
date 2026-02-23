"""
Document Schemas
================
Pydantic/Marshmallow schemas for document validation and serialization.
"""
from typing import Optional, List
from datetime import datetime


class DocumentUploadSchema:
    """Schema for document upload request validation"""

    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'gif'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    VALID_CATEGORIES = [
        'supporting_document',
        'id_proof',
        'tax_document',
        'financial_statement',
        'invoice',
        'other'
    ]

    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in DocumentUploadSchema.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_category(category: str) -> str:
        """Validate and return category, defaulting to 'other' if invalid"""
        if category in DocumentUploadSchema.VALID_CATEGORIES:
            return category
        return 'other'


class DocumentResponseSchema:
    """Schema for document response serialization"""

    @staticmethod
    def serialize(document, include_uploader: bool = True) -> dict:
        """Serialize a document object to dict"""
        # Determine the best URL for accessing the file
        file_url = (
            document.external_web_url or
            document.storage_url or
            document.blob_url or
            f'/api/documents/{document.id}/view'
        )

        data = {
            'id': document.id,
            'original_filename': document.original_filename,
            'file_type': document.file_type,
            'file_size': document.file_size,
            'file_size_formatted': DocumentResponseSchema._format_file_size(document.file_size),
            'mime_type': document.mime_type,
            'storage_path': document.storage_path or document.blob_name,
            'storage_url': document.storage_url or document.blob_url,
            'file_url': file_url,
            'storage_type': document.storage_type,
            'company_id': document.company_id,
            'service_request_id': document.service_request_id,
            'document_category': document.document_category,
            'description': document.description,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'external_item_id': document.external_item_id,
            'external_web_url': document.external_web_url,
            'client_folder_name': document.client_folder_name
        }

        if include_uploader and document.uploaded_by:
            data['uploaded_by'] = {
                'id': document.uploaded_by.id,
                'full_name': document.uploaded_by.full_name,
                'email': document.uploaded_by.email
            }

        return data

    @staticmethod
    def _format_file_size(file_size: Optional[int]) -> str:
        """Format file size in human readable format"""
        if not file_size:
            return 'Unknown'

        size = file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class DocumentCategorySchema:
    """Schema for document categories"""

    CATEGORIES = [
        {'value': 'supporting_document', 'label': 'Supporting Document'},
        {'value': 'id_proof', 'label': 'ID Proof'},
        {'value': 'tax_document', 'label': 'Tax Document'},
        {'value': 'financial_statement', 'label': 'Financial Statement'},
        {'value': 'invoice', 'label': 'Invoice'},
        {'value': 'other', 'label': 'Other'},
    ]

    @staticmethod
    def get_all() -> List[dict]:
        """Get all document categories"""
        return DocumentCategorySchema.CATEGORIES

    @staticmethod
    def is_valid(category: str) -> bool:
        """Check if category is valid"""
        return any(c['value'] == category for c in DocumentCategorySchema.CATEGORIES)


class DocumentListSchema:
    """Schema for document list response"""

    @staticmethod
    def serialize(documents: list, include_uploader: bool = True) -> List[dict]:
        """Serialize a list of documents"""
        return [
            DocumentResponseSchema.serialize(doc, include_uploader)
            for doc in documents
        ]


class SharingLinkResponseSchema:
    """Schema for sharing link response"""

    @staticmethod
    def serialize(link: str, expires_in_hours: int = 168) -> dict:
        """Serialize sharing link response"""
        return {
            'success': True,
            'link': link,
            'expires_in_hours': expires_in_hours
        }


class DownloadUrlResponseSchema:
    """Schema for download URL response"""

    @staticmethod
    def serialize(download_url: str, filename: str, web_url: Optional[str] = None) -> dict:
        """Serialize download URL response"""
        result = {
            'success': True,
            'download_url': download_url,
            'filename': filename
        }
        if web_url:
            result['web_url'] = web_url
        return result
