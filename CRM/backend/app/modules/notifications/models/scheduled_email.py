"""
ScheduledEmail Model - Emails scheduled for future delivery
"""
from datetime import datetime
from app.extensions import db


class ScheduledEmail(db.Model):
    """Model for scheduled emails to be sent at a future time"""
    __tablename__ = 'scheduled_emails'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Recipients
    recipient_type = db.Column(db.String(20), nullable=False)  # single, group, filter
    recipient_email = db.Column(db.String(255))  # For single recipient
    recipient_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))  # For single user
    recipient_filter = db.Column(db.JSON)  # Filter criteria for bulk (role, status, tags, etc.)

    # Email content
    subject = db.Column(db.String(500), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id', ondelete='SET NULL'))
    template_context = db.Column(db.JSON)  # Variables for template rendering

    # Scheduling
    scheduled_at = db.Column(db.DateTime, nullable=False)  # When to send
    timezone = db.Column(db.String(50), default='UTC')

    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, processing, sent, failed, cancelled
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    recipients_count = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)

    # Metadata
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('scheduled_emails', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_scheduled_emails')
    recipient_user = db.relationship('User', foreign_keys=[recipient_user_id])
    template = db.relationship('EmailTemplate', backref='scheduled_emails')

    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    # Recipient type constants
    RECIPIENT_SINGLE = 'single'
    RECIPIENT_GROUP = 'group'
    RECIPIENT_FILTER = 'filter'

    def cancel(self):
        """Cancel the scheduled email"""
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_CANCELLED
            db.session.commit()
            return True
        return False

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'recipient_type': self.recipient_type,
            'subject': self.subject,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'timezone': self.timezone,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'recipients_count': self.recipients_count,
            'sent_count': self.sent_count,
            'failed_count': self.failed_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_details:
            data['body_html'] = self.body_html
            data['recipient_email'] = self.recipient_email
            data['recipient_filter'] = self.recipient_filter
            data['template_id'] = self.template_id
            data['template_context'] = self.template_context
            data['error_message'] = self.error_message
            if self.creator:
                data['created_by'] = {
                    'id': self.creator.id,
                    'name': self.creator.full_name
                }

        return data

    def __repr__(self):
        return f'<ScheduledEmail {self.id} scheduled for {self.scheduled_at}>'
