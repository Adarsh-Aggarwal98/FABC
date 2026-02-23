"""
ServiceRequest Model - Service request from a user
"""
import uuid
from datetime import datetime
from app.extensions import db


class ServiceRequest(db.Model):
    """Service request from a user"""
    __tablename__ = 'service_requests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    assigned_accountant_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Client entity (organization this request is for) - optional for backwards compatibility
    client_entity_id = db.Column(db.String(36), db.ForeignKey('client_entities.id', ondelete='SET NULL'), nullable=True)

    # Auto-generated request number for easy identification (REQ-000001)
    request_number = db.Column(db.String(20), unique=True, index=True)

    # Request description (client can describe what they need)
    description = db.Column(db.Text)

    # Status (kept for backward compatibility - synced with workflow step name)
    status = db.Column(db.String(50), default='pending')

    # Workflow step - current position in the workflow
    current_step_id = db.Column(db.String(36), db.ForeignKey('workflow_steps.id'), nullable=True)

    # Internal notes (visible only to accountants)
    internal_notes = db.Column(db.Text)

    # Invoice tracking
    invoice_raised = db.Column(db.Boolean, default=False)
    invoice_paid = db.Column(db.Boolean, default=False)
    invoice_amount = db.Column(db.Numeric(10, 2))
    payment_link = db.Column(db.String(500))

    # External system reference (e.g., Xero, XPM)
    xero_reference_job_id = db.Column(db.String(100))  # External job/request ID from client
    internal_reference = db.Column(db.String(100))  # Practice's internal reference number

    # Deadline and Priority
    deadline_date = db.Column(db.Date)  # When the job should be completed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent

    # Cost tracking
    actual_cost = db.Column(db.Numeric(10, 2))  # Actual cost incurred for this job
    cost_notes = db.Column(db.Text)  # Notes about the costs
    labor_hours = db.Column(db.Numeric(6, 2), default=0)  # Hours spent on this job
    labor_rate = db.Column(db.Numeric(10, 2))  # Hourly rate used

    # Priority constants
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_HIGH, PRIORITY_URGENT]

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='service_requests')
    assigned_accountant = db.relationship('User', foreign_keys=[assigned_accountant_id],
                                          backref='assigned_requests')
    queries = db.relationship('Query', backref='service_request', lazy='dynamic',
                              cascade='all, delete-orphan')
    client_entity = db.relationship('ClientEntity', backref=db.backref('service_requests', lazy='dynamic'))

    # Status constants
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_INVOICE_RAISED = 'invoice_raised'
    STATUS_ASSIGNED = 'assigned'
    STATUS_QUERY_RAISED = 'query_raised'
    STATUS_ACCOUNTANT_REVIEW_PENDING = 'accountant_review_pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'

    VALID_STATUSES = [
        STATUS_DRAFT, STATUS_PENDING, STATUS_INVOICE_RAISED, STATUS_ASSIGNED, STATUS_QUERY_RAISED,
        STATUS_ACCOUNTANT_REVIEW_PENDING, STATUS_PROCESSING, STATUS_COMPLETED
    ]

    @staticmethod
    def generate_request_number():
        """Generate a unique sequential request number like REQ-000001"""
        # Get the highest existing request number
        last_request = ServiceRequest.query.filter(
            ServiceRequest.request_number.isnot(None)
        ).order_by(ServiceRequest.request_number.desc()).first()

        if last_request and last_request.request_number:
            # Extract the number part and increment
            try:
                last_num = int(last_request.request_number.split('-')[1])
                new_num = last_num + 1
            except (IndexError, ValueError):
                new_num = 1
        else:
            new_num = 1

        return f'REQ-{new_num:06d}'

    def to_dict(self, include_user=True, include_accountant=True, include_notes=False, include_cost=False):
        data = {
            'id': self.id,
            'request_number': self.request_number,
            'description': self.description,
            'service': self.service.to_dict() if self.service else None,
            'status': self.status,
            'current_step_id': self.current_step_id,
            'invoice_raised': self.invoice_raised,
            'invoice_paid': self.invoice_paid,
            'invoice_amount': float(self.invoice_amount) if self.invoice_amount else None,
            'payment_link': self.payment_link if self.invoice_raised else None,
            'xero_reference_job_id': self.xero_reference_job_id,
            'internal_reference': self.internal_reference,
            'deadline_date': self.deadline_date.isoformat() if self.deadline_date else None,
            'priority': self.priority,
            'is_overdue': self.deadline_date and self.deadline_date < datetime.utcnow().date() and self.status != self.STATUS_COMPLETED,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

        # Cost tracking (only for admin/accountant views)
        if include_cost:
            data['actual_cost'] = float(self.actual_cost) if self.actual_cost else None
            data['cost_notes'] = self.cost_notes
            data['labor_hours'] = float(self.labor_hours) if self.labor_hours else 0
            data['labor_rate'] = float(self.labor_rate) if self.labor_rate else None
            # Calculate profit margin if we have both revenue and cost
            if self.invoice_amount and self.actual_cost:
                revenue = float(self.invoice_amount)
                cost = float(self.actual_cost)
                data['profit'] = revenue - cost
                data['profit_margin'] = ((revenue - cost) / revenue * 100) if revenue > 0 else 0

        if include_user:
            data['user'] = {
                'id': self.user.id,
                'email': self.user.email,
                'full_name': self.user.full_name
            }

        if include_accountant and self.assigned_accountant:
            data['assigned_accountant'] = {
                'id': self.assigned_accountant.id,
                'email': self.assigned_accountant.email,
                'full_name': self.assigned_accountant.full_name
            }

        # Internal notes only for accountants/admins
        if include_notes:
            data['internal_notes'] = self.internal_notes

        # Client entity (organization this request is for)
        if self.client_entity:
            data['client_entity'] = {
                'id': self.client_entity.id,
                'name': self.client_entity.name,
                'entity_type': self.client_entity.entity_type,
                'abn': self.client_entity.abn
            }
        else:
            data['client_entity'] = None
        data['client_entity_id'] = self.client_entity_id

        return data

    def __repr__(self):
        return f'<ServiceRequest {self.id}>'
