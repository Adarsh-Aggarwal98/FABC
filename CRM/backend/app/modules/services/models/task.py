"""
Task Model - Tasks that can be assigned to accountants
"""
from datetime import datetime
import uuid
from app.extensions import db


class Task(db.Model):
    """Tasks that can be assigned to accountants, optionally linked to service requests"""
    __tablename__ = 'tasks'

    # Status constants (unified with request statuses)
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_REVIEW = 'review'
    STATUS_COMPLETED = 'completed'

    # Legacy aliases for backward compatibility
    STATUS_TODO = STATUS_PENDING
    STATUS_DONE = STATUS_COMPLETED

    VALID_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_REVIEW, STATUS_COMPLETED]

    # Priority constants
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_HIGH, PRIORITY_URGENT]

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Assignment
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Optional link to service request
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id', ondelete='SET NULL'), nullable=True)

    # Task details
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.String(20), default=PRIORITY_NORMAL)
    due_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Time tracking
    estimated_minutes = db.Column(db.Integer, nullable=True)
    actual_minutes = db.Column(db.Integer, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('tasks', lazy='dynamic'))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref=db.backref('tasks_created', lazy='dynamic'))
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref=db.backref('tasks_assigned', lazy='dynamic'))
    service_request = db.relationship('ServiceRequest', backref=db.backref('tasks', lazy='dynamic'))

    def to_dict(self, include_relationships=True):
        """Convert task to dictionary"""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_minutes': self.estimated_minutes,
            'actual_minutes': self.actual_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relationships:
            # Created by
            if self.created_by:
                data['created_by'] = {
                    'id': self.created_by.id,
                    'email': self.created_by.email,
                    'full_name': self.created_by.full_name,
                    'first_name': self.created_by.first_name,
                }

            # Assigned to
            if self.assigned_to:
                data['assigned_to'] = {
                    'id': self.assigned_to.id,
                    'email': self.assigned_to.email,
                    'full_name': self.assigned_to.full_name,
                    'first_name': self.assigned_to.first_name,
                }
            else:
                data['assigned_to'] = None

            # Service request (if linked)
            if self.service_request:
                data['service_request'] = {
                    'id': self.service_request.id,
                    'request_number': self.service_request.request_number,
                    'status': self.service_request.status,
                }
            else:
                data['service_request'] = None

        return data

    def __repr__(self):
        return f'<Task {self.id}: {self.title[:30]}>'
