"""
ServiceRenewal Model - Tracks recurring service renewals for clients
"""
from datetime import datetime
from app.extensions import db


class ServiceRenewal(db.Model):
    """Tracks recurring service renewals for clients"""
    __tablename__ = 'service_renewals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Last completion
    last_completed_at = db.Column(db.DateTime)
    last_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id', ondelete='SET NULL'))

    # Next renewal
    next_due_date = db.Column(db.Date, nullable=False)

    # Reminder tracking - stores list of sent reminders [{sent_at, days_before, email_id}]
    reminders_sent = db.Column(db.JSON, default=list)
    last_reminder_at = db.Column(db.DateTime)

    # Status: pending, reminded, completed, skipped
    status = db.Column(db.String(20), default='pending')
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('service_renewals', lazy='dynamic'))
    service = db.relationship('Service', backref=db.backref('renewals', lazy='dynamic'))
    company = db.relationship('Company', backref=db.backref('service_renewals', lazy='dynamic'))
    last_request = db.relationship('ServiceRequest', foreign_keys=[last_request_id])

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'service_id', 'next_due_date', name='unique_user_service_due_date'),
    )

    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_REMINDED = 'reminded'
    STATUS_COMPLETED = 'completed'
    STATUS_SKIPPED = 'skipped'

    def record_reminder_sent(self, days_before, email_id=None):
        """Record that a reminder was sent"""
        if self.reminders_sent is None:
            self.reminders_sent = []

        self.reminders_sent.append({
            'sent_at': datetime.utcnow().isoformat(),
            'days_before': days_before,
            'email_id': email_id
        })
        self.last_reminder_at = datetime.utcnow()
        self.status = self.STATUS_REMINDED

    def to_dict(self, include_user=False, include_service=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'company_id': self.company_id,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'last_completed_at': self.last_completed_at.isoformat() if self.last_completed_at else None,
            'last_request_id': self.last_request_id,
            'reminders_sent': self.reminders_sent or [],
            'last_reminder_at': self.last_reminder_at.isoformat() if self.last_reminder_at else None,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'full_name': self.user.full_name,
                'email': self.user.email
            }

        if include_service and self.service:
            data['service'] = {
                'id': self.service.id,
                'name': self.service.name,
                'category': self.service.category
            }

        return data

    def __repr__(self):
        return f'<ServiceRenewal {self.id} user={self.user_id} service={self.service_id}>'
