"""
Audit/Activity Log models
Tracks all important actions in the system for accountability and debugging.
"""
import uuid
from datetime import datetime
from app.extensions import db


class ActivityLog(db.Model):
    """Activity log for tracking user actions across the system"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # What entity was affected
    entity_type = db.Column(db.String(50), nullable=False)  # user, service_request, document, etc.
    entity_id = db.Column(db.String(36), nullable=False)  # ID of the affected entity

    # What action was performed
    action = db.Column(db.String(50), nullable=False)  # created, updated, deleted, assigned, etc.

    # Additional details as JSON
    details = db.Column(db.JSON)  # { old_value: ..., new_value: ..., field: ... }

    # Who performed the action
    performed_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Company scope for filtering
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

    # Request metadata
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    performed_by = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
    company = db.relationship('Company', backref=db.backref('activity_logs', lazy='dynamic'))

    # Common action constants
    ACTION_CREATED = 'created'
    ACTION_UPDATED = 'updated'
    ACTION_DELETED = 'deleted'
    ACTION_ASSIGNED = 'assigned'
    ACTION_UNASSIGNED = 'unassigned'
    ACTION_STATUS_CHANGED = 'status_changed'
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_PASSWORD_CHANGED = 'password_changed'
    ACTION_INVITED = 'invited'
    ACTION_ACTIVATED = 'activated'
    ACTION_DEACTIVATED = 'deactivated'
    ACTION_DOCUMENT_UPLOADED = 'document_uploaded'
    ACTION_DOCUMENT_DOWNLOADED = 'document_downloaded'
    ACTION_NOTE_ADDED = 'note_added'
    ACTION_TAG_ASSIGNED = 'tag_assigned'
    ACTION_TAG_REMOVED = 'tag_removed'
    ACTION_INVOICE_RAISED = 'invoice_raised'
    ACTION_INVOICE_PAID = 'invoice_paid'
    ACTION_FORM_SUBMITTED = 'form_submitted'
    ACTION_EMAIL_SENT = 'email_sent'
    ACTION_IMPERSONATION_STARTED = 'impersonation_started'
    ACTION_IMPERSONATION_ENDED = 'impersonation_ended'

    # Entity type constants
    ENTITY_USER = 'user'
    ENTITY_SERVICE_REQUEST = 'service_request'
    ENTITY_DOCUMENT = 'document'
    ENTITY_COMPANY = 'company'
    ENTITY_TAG = 'tag'
    ENTITY_NOTE = 'note'
    ENTITY_FORM = 'form'
    ENTITY_EMAIL_TEMPLATE = 'email_template'

    def to_dict(self, include_performer=True):
        data = {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_performer and self.performed_by:
            data['performed_by'] = {
                'id': self.performed_by.id,
                'email': self.performed_by.email,
                'full_name': self.performed_by.full_name
            }

        return data

    def __repr__(self):
        return f'<ActivityLog {self.action} on {self.entity_type}:{self.entity_id}>'


class ImpersonationSession(db.Model):
    """
    Tracks SuperAdmin impersonation sessions for audit and support purposes.

    Impersonation allows SuperAdmins to temporarily act as another user
    (typically practice owners) to help troubleshoot issues.
    """
    __tablename__ = 'impersonation_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Who is doing the impersonating (must be super_admin)
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Who is being impersonated
    impersonated_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Session timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)  # NULL means session is still active

    # Reason/context for impersonation (for audit trail)
    reason = db.Column(db.Text)

    # Request metadata
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))

    # Track actions performed during impersonation
    action_count = db.Column(db.Integer, default=0)

    # Relationships
    admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('impersonation_sessions_as_admin', lazy='dynamic'))
    impersonated_user = db.relationship('User', foreign_keys=[impersonated_user_id], backref=db.backref('impersonation_sessions_as_target', lazy='dynamic'))

    @property
    def is_active(self):
        """Check if impersonation session is still active"""
        return self.ended_at is None

    @property
    def duration_seconds(self):
        """Get session duration in seconds"""
        end_time = self.ended_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

    def end_session(self):
        """Mark the session as ended"""
        self.ended_at = datetime.utcnow()

    def to_dict(self, include_users=True):
        data = {
            'id': self.id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'is_active': self.is_active,
            'duration_seconds': self.duration_seconds,
            'reason': self.reason,
            'action_count': self.action_count,
            'ip_address': self.ip_address
        }

        if include_users:
            if self.admin:
                data['admin'] = {
                    'id': self.admin.id,
                    'email': self.admin.email,
                    'full_name': self.admin.full_name
                }
            if self.impersonated_user:
                data['impersonated_user'] = {
                    'id': self.impersonated_user.id,
                    'email': self.impersonated_user.email,
                    'full_name': self.impersonated_user.full_name,
                    'role': self.impersonated_user.role.name if self.impersonated_user.role else None,
                    'company_id': self.impersonated_user.company_id
                }

        return data

    def __repr__(self):
        return f'<ImpersonationSession {self.admin_id} -> {self.impersonated_user_id}>'
