"""
SystemEmailConfig Model
=======================

System-level SMTP email configuration (Super Admin).
"""
from datetime import datetime
from app.extensions import db
from app.modules.company.models.enums import EmailProviderType


class SystemEmailConfig(db.Model):
    """System-level SMTP email configuration (Super Admin)"""
    __tablename__ = 'system_email_config'

    id = db.Column(db.Integer, primary_key=True)

    # Provider type
    provider = db.Column(db.Enum(EmailProviderType), default=EmailProviderType.GMAIL)
    is_enabled = db.Column(db.Boolean, default=False)

    # SMTP Settings
    smtp_host = db.Column(db.String(255))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(255))
    smtp_password = db.Column(db.String(500))
    smtp_use_tls = db.Column(db.Boolean, default=True)
    smtp_use_ssl = db.Column(db.Boolean, default=False)

    # Sender information
    sender_email = db.Column(db.String(255))
    sender_name = db.Column(db.String(255), default='Accountant CRM')

    # Whether to use this as fallback when company config fails
    use_as_fallback = db.Column(db.Boolean, default=True)

    # Status tracking
    last_test_at = db.Column(db.DateTime)
    last_test_success = db.Column(db.Boolean)
    last_error = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_config(cls):
        """Get the system email config (singleton)"""
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'provider': self.provider.value if self.provider else None,
            'is_enabled': self.is_enabled,
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_use_tls': self.smtp_use_tls,
            'smtp_use_ssl': self.smtp_use_ssl,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'use_as_fallback': self.use_as_fallback,
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
        return f'<SystemEmailConfig {self.provider.value if self.provider else "N/A"}>'
