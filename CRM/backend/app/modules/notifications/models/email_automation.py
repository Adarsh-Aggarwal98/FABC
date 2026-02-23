"""
EmailAutomation Model - Automated email triggers based on events
"""
from datetime import datetime
from app.extensions import db


class EmailAutomation(db.Model):
    """Model for automated email triggers based on events"""
    __tablename__ = 'email_automations'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Trigger configuration
    trigger_type = db.Column(db.String(50), nullable=False)  # See TRIGGER_* constants below
    trigger_config = db.Column(db.JSON)  # Additional trigger parameters

    # Email configuration
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id', ondelete='SET NULL'))
    custom_subject = db.Column(db.String(500))  # Override template subject
    custom_body = db.Column(db.Text)  # Override template body
    delay_minutes = db.Column(db.Integer, default=0)  # Delay before sending (0 = immediate)

    # Conditions
    conditions = db.Column(db.JSON)  # Additional conditions to check before sending

    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_triggered_at = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('email_automations', lazy='dynamic'))
    template = db.relationship('EmailTemplate', backref='automations')
    creator = db.relationship('User', backref='created_automations')

    # Trigger type constants
    TRIGGER_CLIENT_REGISTERED = 'client_registered'  # When a new client signs up
    TRIGGER_SERVICE_REQUESTED = 'service_requested'  # When a service request is created
    TRIGGER_SERVICE_COMPLETED = 'service_completed'  # When a service is marked complete
    TRIGGER_INVOICE_SENT = 'invoice_sent'  # When an invoice is sent
    TRIGGER_INVOICE_OVERDUE = 'invoice_overdue'  # When invoice becomes overdue
    TRIGGER_PAYMENT_RECEIVED = 'payment_received'  # When a payment is received
    TRIGGER_DOCUMENT_UPLOADED = 'document_uploaded'  # When client uploads a document
    TRIGGER_QUERY_RAISED = 'query_raised'  # When a query is raised
    TRIGGER_BIRTHDAY = 'birthday'  # On client's birthday
    TRIGGER_ANNIVERSARY = 'anniversary'  # On client's anniversary with the company
    TRIGGER_INACTIVITY = 'inactivity'  # When client hasn't been active for X days
    TRIGGER_CUSTOM = 'custom'  # Custom webhook trigger

    VALID_TRIGGERS = [
        TRIGGER_CLIENT_REGISTERED,
        TRIGGER_SERVICE_REQUESTED,
        TRIGGER_SERVICE_COMPLETED,
        TRIGGER_INVOICE_SENT,
        TRIGGER_INVOICE_OVERDUE,
        TRIGGER_PAYMENT_RECEIVED,
        TRIGGER_DOCUMENT_UPLOADED,
        TRIGGER_QUERY_RAISED,
        TRIGGER_BIRTHDAY,
        TRIGGER_ANNIVERSARY,
        TRIGGER_INACTIVITY,
        TRIGGER_CUSTOM
    ]

    @classmethod
    def get_automations_for_trigger(cls, company_id, trigger_type):
        """Get all active automations for a specific trigger"""
        return cls.query.filter_by(
            company_id=company_id,
            trigger_type=trigger_type,
            is_active=True
        ).all()

    def increment_trigger_count(self):
        """Increment the trigger count and update last triggered timestamp"""
        self.trigger_count += 1
        self.last_triggered_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self, include_template=False):
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'trigger_type': self.trigger_type,
            'trigger_config': self.trigger_config,
            'template_id': self.template_id,
            'custom_subject': self.custom_subject,
            'delay_minutes': self.delay_minutes,
            'conditions': self.conditions,
            'is_active': self.is_active,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'trigger_count': self.trigger_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_template and self.template:
            data['template'] = {
                'id': self.template.id,
                'name': self.template.name,
                'slug': self.template.slug
            }

        return data

    def __repr__(self):
        return f'<EmailAutomation {self.name} ({self.trigger_type})>'


class EmailAutomationLog(db.Model):
    """Log of automation triggers for audit and debugging"""
    __tablename__ = 'email_automation_logs'

    id = db.Column(db.Integer, primary_key=True)
    automation_id = db.Column(db.Integer, db.ForeignKey('email_automations.id', ondelete='CASCADE'), nullable=False)
    recipient_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))
    recipient_email = db.Column(db.String(255), nullable=False)

    # Trigger context
    trigger_data = db.Column(db.JSON)  # Data that triggered the automation

    # Result
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed, skipped
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    automation = db.relationship('EmailAutomation', backref=db.backref('logs', lazy='dynamic'))
    recipient = db.relationship('User', backref='automation_emails')

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_SKIPPED = 'skipped'  # Skipped due to conditions not met

    def to_dict(self):
        return {
            'id': self.id,
            'automation_id': self.automation_id,
            'recipient_email': self.recipient_email,
            'trigger_data': self.trigger_data,
            'status': self.status,
            'error_message': self.error_message,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<EmailAutomationLog {self.id} for automation {self.automation_id}>'
