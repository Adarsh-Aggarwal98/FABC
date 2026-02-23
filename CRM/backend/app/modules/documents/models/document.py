"""
Document Model
==============
SQLAlchemy model for storing file metadata and storage references.
Supports multiple storage backends: Google Drive, SharePoint, Azure Blob, Zoho Drive, Local filesystem.
"""
import uuid
from datetime import datetime
from app.extensions import db


class Document(db.Model):
    """Document model for storing file metadata and storage references"""
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # File information
    original_filename = db.Column(db.String(500), nullable=False)
    stored_filename = db.Column(db.String(500), nullable=False)  # Unique filename in storage
    file_type = db.Column(db.String(50))  # pdf, jpg, png, etc.
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))

    # Storage information (generic - works with any storage provider)
    storage_path = db.Column(db.String(1000))  # Path/ID in storage (Google Drive ID, SharePoint path, blob path, local path)
    storage_url = db.Column(db.String(1000))  # URL to access the file
    storage_type = db.Column(db.String(50), default='local')  # 'google_drive', 'zoho_drive', 'sharepoint', 'blob', 'local'

    # Legacy columns (kept for backward compatibility, mapped to new names)
    blob_name = db.Column(db.String(1000))  # Deprecated - use storage_path
    blob_url = db.Column(db.String(1000))  # Deprecated - use storage_url

    # Provider-specific fields
    external_item_id = db.Column(db.String(255))  # External ID (Google Drive file ID, SharePoint item ID, Zoho file ID)
    external_web_url = db.Column(db.String(1000))  # Web URL for browser access
    client_folder_name = db.Column(db.String(255))  # Client name used for folder organization

    # Relationships
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=True)
    uploaded_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id'), nullable=True)

    # Document category/type
    document_category = db.Column(db.String(100))  # supporting_doc, id_proof, tax_document, etc.
    description = db.Column(db.Text)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref='documents')
    uploaded_by = db.relationship('User', backref='uploaded_documents')
    service_request = db.relationship('ServiceRequest', backref='documents')

    # Document categories
    CATEGORY_SUPPORTING = 'supporting_document'
    CATEGORY_ID_PROOF = 'id_proof'
    CATEGORY_TAX_DOCUMENT = 'tax_document'
    CATEGORY_FINANCIAL_STATEMENT = 'financial_statement'
    CATEGORY_INVOICE = 'invoice'
    CATEGORY_OTHER = 'other'

    VALID_CATEGORIES = [
        CATEGORY_SUPPORTING, CATEGORY_ID_PROOF, CATEGORY_TAX_DOCUMENT,
        CATEGORY_FINANCIAL_STATEMENT, CATEGORY_INVOICE, CATEGORY_OTHER
    ]

    def to_dict(self, include_uploader=True, include_download_url=False):
        # Determine the best URL for accessing the file
        file_url = self.external_web_url or self.storage_url or self.blob_url or f'/api/documents/{self.id}/view'

        data = {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_size_formatted': self._format_file_size(),
            'mime_type': self.mime_type,
            'storage_path': self.storage_path or self.blob_name,  # New name with fallback
            'storage_url': self.storage_url or self.blob_url,  # New name with fallback
            'file_url': file_url,  # Best URL for accessing the file
            'storage_type': self.storage_type,
            'company_id': self.company_id,
            'service_request_id': self.service_request_id,
            'document_category': self.document_category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'external_item_id': self.external_item_id,
            'external_web_url': self.external_web_url,
            'client_folder_name': self.client_folder_name
        }

        if include_uploader and self.uploaded_by:
            data['uploaded_by'] = {
                'id': self.uploaded_by.id,
                'full_name': self.uploaded_by.full_name,
                'email': self.uploaded_by.email
            }

        return data

    def _format_file_size(self):
        """Format file size in human readable format"""
        if not self.file_size:
            return 'Unknown'

        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def __repr__(self):
        return f'<Document {self.original_filename}>'
