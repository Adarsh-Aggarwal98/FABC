"""
JobNote Model - Notes/history entries for service requests (job tracking)
"""
from datetime import datetime
from app.extensions import db


class JobNote(db.Model):
    """Notes/history entries for service requests (job tracking)"""
    __tablename__ = 'job_notes'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Note type for categorization
    note_type = db.Column(db.String(50), default='general')  # general, status_update, time_entry, client_communication, internal
    content = db.Column(db.Text, nullable=False)

    # Time tracking (optional)
    time_spent_minutes = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('job_notes', lazy='dynamic', order_by='JobNote.created_at.desc()'))
    created_by = db.relationship('User', backref='job_notes_created')

    # Note type constants
    TYPE_GENERAL = 'general'
    TYPE_STATUS_UPDATE = 'status_update'
    TYPE_TIME_ENTRY = 'time_entry'
    TYPE_CLIENT_COMMUNICATION = 'client_communication'
    TYPE_INTERNAL = 'internal'

    VALID_TYPES = [TYPE_GENERAL, TYPE_STATUS_UPDATE, TYPE_TIME_ENTRY, TYPE_CLIENT_COMMUNICATION, TYPE_INTERNAL]

    def to_dict(self, include_creator=True):
        data = {
            'id': self.id,
            'service_request_id': self.service_request_id,
            'note_type': self.note_type,
            'content': self.content,
            'time_spent_minutes': self.time_spent_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_creator and self.created_by:
            data['created_by'] = {
                'id': self.created_by.id,
                'email': self.created_by.email,
                'full_name': self.created_by.full_name
            }

        return data

    def __repr__(self):
        return f'<JobNote {self.id} for request {self.service_request_id}>'
