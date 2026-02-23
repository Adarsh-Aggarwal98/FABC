"""
CompanyEmailConfig Model
========================

SMTP email configuration for a company.
"""
import uuid
from datetime import datetime
from app.extensions import db
from app.modules.company.models.enums import EmailProviderType


class CompanyEmailConfig(db.Model):
    """SMTP email configuration for a company"""
    __tablename__ = 'company_email_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Provider type
    provider = db.Column(db.Enum(EmailProviderType), default=EmailProviderType.GMAIL)
    is_enabled = db.Column(db.Boolean, default=False)

    # SMTP Settings
    smtp_host = db.Column(db.String(255))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(255))
    smtp_password = db.Column(db.String(500))  # Should be encrypted in production
    smtp_use_tls = db.Column(db.Boolean, default=True)
    smtp_use_ssl = db.Column(db.Boolean, default=False)

    # Sender information
    sender_email = db.Column(db.String(255))
    sender_name = db.Column(db.String(255))
    reply_to_email = db.Column(db.String(255))

    # OAuth tokens for Gmail/Outlook (alternative to password)
    oauth_access_token = db.Column(db.Text)
    oauth_refresh_token = db.Column(db.Text)
    oauth_token_expires_at = db.Column(db.DateTime)

    # Status tracking
    last_test_at = db.Column(db.DateTime)
    last_test_success = db.Column(db.Boolean)
    last_error = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    company = db.relationship('Company', backref=db.backref('email_config', uselist=False))

    # Pre-configured SMTP settings for common providers
    PROVIDER_SETTINGS = {
        'GMAIL': {
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_use_tls': True,
            'smtp_use_ssl': False
        },
        'OUTLOOK': {
            'smtp_host': 'smtp.office365.com',
            'smtp_port': 587,
            'smtp_use_tls': True,
            'smtp_use_ssl': False
        },
        'ZOHO': {
            'smtp_host': 'smtp.zoho.com',
            'smtp_port': 587,
            'smtp_use_tls': True,
            'smtp_use_ssl': False
        }
    }

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'provider': self.provider.value if self.provider else None,
            'is_enabled': self.is_enabled,
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_use_tls': self.smtp_use_tls,
            'smtp_use_ssl': self.smtp_use_ssl,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'reply_to_email': self.reply_to_email,
            'last_test_at': self.last_test_at.isoformat() if self.last_test_at else None,
            'last_test_success': self.last_test_success,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_sensitive:
            data['smtp_password'] = self.smtp_password
        return data

    def __repr__(self):
        return f'<CompanyEmailConfig {self.company_id} - {self.provider.value if self.provider else "N/A"}>'
