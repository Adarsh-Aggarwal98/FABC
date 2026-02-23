"""
CompanyStorageConfig Model
==========================

Storage provider configuration for a company.
"""
import uuid
from datetime import datetime
from app.extensions import db
from app.modules.company.models.enums import StorageProviderType


class CompanyStorageConfig(db.Model):
    """Storage provider configuration for a company"""
    __tablename__ = 'company_storage_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Provider type
    provider = db.Column(db.Enum(StorageProviderType), default=StorageProviderType.AZURE_BLOB)
    is_enabled = db.Column(db.Boolean, default=False)

    # SharePoint Settings
    sharepoint_site_id = db.Column(db.String(255))
    sharepoint_drive_id = db.Column(db.String(255))
    sharepoint_root_folder = db.Column(db.String(255), default='CRM_Documents')

    # Zoho Drive Settings
    zoho_client_id = db.Column(db.String(255))
    zoho_client_secret = db.Column(db.String(500))
    zoho_access_token = db.Column(db.Text)
    zoho_refresh_token = db.Column(db.Text)
    zoho_token_expires_at = db.Column(db.DateTime)
    zoho_root_folder_id = db.Column(db.String(255))
    zoho_org_id = db.Column(db.String(255))

    # Google Drive Settings
    google_client_id = db.Column(db.String(255))
    google_client_secret = db.Column(db.String(500))
    google_access_token = db.Column(db.Text)
    google_refresh_token = db.Column(db.Text)
    google_token_expires_at = db.Column(db.DateTime)
    google_root_folder_id = db.Column(db.String(255))  # Folder ID where documents will be stored

    # Azure Blob Settings (if company wants their own storage)
    azure_connection_string = db.Column(db.Text)
    azure_container_name = db.Column(db.String(255))

    # Status tracking
    last_sync_at = db.Column(db.DateTime)
    last_error = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    company = db.relationship('Company', backref=db.backref('storage_config', uselist=False))

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'provider': self.provider.value if self.provider else None,
            'is_enabled': self.is_enabled,
            'sharepoint_site_id': self.sharepoint_site_id,
            'sharepoint_drive_id': self.sharepoint_drive_id,
            'sharepoint_root_folder': self.sharepoint_root_folder,
            'zoho_client_id': self.zoho_client_id,
            'zoho_root_folder_id': self.zoho_root_folder_id,
            'zoho_org_id': self.zoho_org_id,
            'zoho_connected': bool(self.zoho_access_token or self.zoho_refresh_token),
            'google_client_id': self.google_client_id,
            'google_root_folder_id': self.google_root_folder_id,
            'google_connected': bool(self.google_access_token or self.google_refresh_token),
            'azure_container_name': self.azure_container_name,
            'azure_configured': bool(self.azure_connection_string),
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_sensitive:
            data['zoho_client_secret'] = self.zoho_client_secret
            data['google_client_secret'] = self.google_client_secret
            data['azure_connection_string'] = self.azure_connection_string
        return data

    def __repr__(self):
        return f'<CompanyStorageConfig {self.company_id} - {self.provider.value if self.provider else "N/A"}>'
