"""
RequestAuditLog Model - Audit log for tracking changes to service requests
"""
from datetime import datetime
from app.extensions import db


class RequestAuditLog(db.Model):
    """Audit log for tracking changes to service requests"""
    __tablename__ = 'request_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    modified_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # What was changed
    field_name = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)

    # When
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('audit_logs', lazy='dynamic', order_by='RequestAuditLog.created_at.desc()'))
    modified_by = db.relationship('User', backref='request_modifications')

    # Field display names for UI
    FIELD_LABELS = {
        'status': 'Status',
        'assigned_accountant_id': 'Assigned Accountant',
        'internal_notes': 'Internal Notes',
        'invoice_raised': 'Invoice Raised',
        'invoice_paid': 'Invoice Paid',
        'invoice_amount': 'Invoice Amount',
        'payment_link': 'Payment Link',
        'xero_reference_job_id': 'Xero Job ID',
        'internal_reference': 'Internal Reference',
    }

    @classmethod
    def log_change(cls, request_id, user_id, field_name, old_value, new_value):
        """Create an audit log entry for a field change"""
        if str(old_value) != str(new_value):  # Only log actual changes
            log = cls(
                service_request_id=request_id,
                modified_by_id=user_id,
                field_name=field_name,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None
            )
            db.session.add(log)
            return log
        return None

    @classmethod
    def log_changes(cls, request_id, user_id, changes: dict):
        """Log multiple field changes at once"""
        logs = []
        for field_name, (old_val, new_val) in changes.items():
            log = cls.log_change(request_id, user_id, field_name, old_val, new_val)
            if log:
                logs.append(log)
        return logs

    def to_dict(self, include_user=True):
        data = {
            'id': self.id,
            'service_request_id': self.service_request_id,
            'field_name': self.field_name,
            'field_label': self.FIELD_LABELS.get(self.field_name, self.field_name),
            'old_value': self.old_value,
            'new_value': self.new_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_user and self.modified_by:
            data['modified_by'] = {
                'id': self.modified_by.id,
                'email': self.modified_by.email,
                'full_name': self.modified_by.full_name,
                'role': self.modified_by.role.name
            }

        return data

    def __repr__(self):
        return f'<RequestAuditLog {self.field_name} changed on {self.service_request_id}>'
