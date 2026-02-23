"""
Workflow Models for Custom Service Workflows

These models allow practice owners to create custom workflows for each service,
with configurable steps, transitions, and automation actions.
"""
import uuid
import enum
from datetime import datetime
from app.extensions import db


class StepType(enum.Enum):
    """Types of workflow steps"""
    START = "START"      # Initial step (e.g., pending)
    NORMAL = "NORMAL"    # Regular step
    QUERY = "QUERY"      # Waiting for client input
    END = "END"          # Terminal step (e.g., completed)


class ServiceWorkflow(db.Model):
    """Custom workflow template for services"""
    __tablename__ = 'service_workflows'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=True)  # NULL for default workflow
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)  # System default workflow
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Relationships
    steps = db.relationship('WorkflowStep', backref='workflow', cascade='all, delete-orphan',
                           lazy='dynamic', order_by='WorkflowStep.order')
    transitions = db.relationship('WorkflowTransition', backref='workflow',
                                  cascade='all, delete-orphan', lazy='dynamic')
    automations = db.relationship('WorkflowAutomation', backref='workflow',
                                  cascade='all, delete-orphan', lazy='dynamic')
    services = db.relationship('Service', backref='custom_workflow', lazy='dynamic')
    company = db.relationship('Company', backref=db.backref('workflows', lazy='dynamic'))
    created_by = db.relationship('User', backref='created_workflows')

    def get_start_step(self):
        """Get the START step of this workflow"""
        return WorkflowStep.query.filter_by(
            workflow_id=self.id,
            step_type=StepType.START
        ).first()

    def get_end_steps(self):
        """Get all END steps of this workflow"""
        return WorkflowStep.query.filter_by(
            workflow_id=self.id,
            step_type=StepType.END
        ).all()

    def to_dict(self, include_steps=True, include_transitions=True):
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'service_count': self.services.count()
        }

        if include_steps:
            data['steps'] = [step.to_dict() for step in self.steps.order_by(WorkflowStep.order).all()]

        if include_transitions:
            data['transitions'] = [t.to_dict() for t in self.transitions.all()]

        return data

    def __repr__(self):
        return f'<ServiceWorkflow {self.name}>'


class WorkflowStep(db.Model):
    """Individual step in a workflow"""
    __tablename__ = 'workflow_steps'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('service_workflows.id', ondelete='CASCADE'), nullable=False)

    # Step definition
    name = db.Column(db.String(50), nullable=False)  # Internal name (used for status sync)
    display_name = db.Column(db.String(100))  # UI label
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='blue')  # Badge color
    icon = db.Column(db.String(50))  # Optional icon name

    # Step type
    step_type = db.Column(db.Enum(StepType), default=StepType.NORMAL)
    order = db.Column(db.Integer, default=0)

    # Permissions
    allowed_roles = db.Column(db.JSON)  # ['admin', 'accountant']
    required_fields = db.Column(db.JSON)  # Fields required before leaving step

    # Automation flags
    auto_assign = db.Column(db.Boolean, default=False)
    notify_roles = db.Column(db.JSON)  # Roles to notify on enter
    notify_client = db.Column(db.Boolean, default=False)

    # Position in visual builder (for ReactFlow)
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships for transitions
    outgoing_transitions = db.relationship(
        'WorkflowTransition',
        foreign_keys='WorkflowTransition.from_step_id',
        backref='from_step',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    incoming_transitions = db.relationship(
        'WorkflowTransition',
        foreign_keys='WorkflowTransition.to_step_id',
        backref='to_step',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'name': self.name,
            'display_name': self.display_name or self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'step_type': self.step_type.value if self.step_type else 'NORMAL',
            'order': self.order,
            'allowed_roles': self.allowed_roles or [],
            'required_fields': self.required_fields or [],
            'auto_assign': self.auto_assign,
            'notify_roles': self.notify_roles or [],
            'notify_client': self.notify_client,
            'position_x': self.position_x,
            'position_y': self.position_y
        }

    def __repr__(self):
        return f'<WorkflowStep {self.name}>'


class WorkflowTransition(db.Model):
    """Valid transitions between steps"""
    __tablename__ = 'workflow_transitions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('service_workflows.id', ondelete='CASCADE'), nullable=False)
    from_step_id = db.Column(db.String(36), db.ForeignKey('workflow_steps.id', ondelete='CASCADE'), nullable=False)
    to_step_id = db.Column(db.String(36), db.ForeignKey('workflow_steps.id', ondelete='CASCADE'), nullable=False)

    # Transition metadata
    name = db.Column(db.String(100))  # Button label (e.g., "Approve", "Send for Review")
    description = db.Column(db.Text)

    # Conditions
    requires_invoice_raised = db.Column(db.Boolean, default=False)
    requires_invoice_paid = db.Column(db.Boolean, default=False)
    requires_assignment = db.Column(db.Boolean, default=False)
    allowed_roles = db.Column(db.JSON)  # Who can trigger this transition

    # Actions
    send_notification = db.Column(db.Boolean, default=True)
    notification_template = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'from_step_id': self.from_step_id,
            'to_step_id': self.to_step_id,
            'name': self.name,
            'description': self.description,
            'requires_invoice_raised': self.requires_invoice_raised,
            'requires_invoice_paid': self.requires_invoice_paid,
            'requires_assignment': self.requires_assignment,
            'allowed_roles': self.allowed_roles or [],
            'send_notification': self.send_notification,
            'notification_template': self.notification_template
        }

    def __repr__(self):
        return f'<WorkflowTransition {self.from_step_id} -> {self.to_step_id}>'


class WorkflowAutomation(db.Model):
    """Automation rules triggered on step transitions"""
    __tablename__ = 'workflow_automations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey('service_workflows.id', ondelete='CASCADE'), nullable=False)
    step_id = db.Column(db.String(36), db.ForeignKey('workflow_steps.id', ondelete='CASCADE'), nullable=True)

    # Trigger type
    trigger = db.Column(db.String(20), nullable=False)  # 'on_enter', 'on_exit', 'after_duration'

    # Action configuration
    action_type = db.Column(db.String(50), nullable=False)  # 'notify', 'assign', 'webhook', 'email', 'update_field'
    action_config = db.Column(db.JSON)  # Action-specific config

    # Conditions (optional)
    conditions = db.Column(db.JSON)  # Optional conditions to check before executing

    # For time-based triggers
    delay_minutes = db.Column(db.Integer)  # Wait before executing (for 'after_duration' trigger)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    step = db.relationship('WorkflowStep', backref=db.backref('automations', lazy='dynamic'))

    # Trigger type constants
    TRIGGER_ON_ENTER = 'on_enter'
    TRIGGER_ON_EXIT = 'on_exit'
    TRIGGER_AFTER_DURATION = 'after_duration'

    VALID_TRIGGERS = [TRIGGER_ON_ENTER, TRIGGER_ON_EXIT, TRIGGER_AFTER_DURATION]

    # Action type constants
    ACTION_NOTIFY = 'notify'
    ACTION_ASSIGN = 'auto_assign'
    ACTION_WEBHOOK = 'webhook'
    ACTION_EMAIL = 'email'
    ACTION_UPDATE_FIELD = 'update_field'
    ACTION_CREATE_TASK = 'create_task'

    VALID_ACTIONS = [ACTION_NOTIFY, ACTION_ASSIGN, ACTION_WEBHOOK, ACTION_EMAIL, ACTION_UPDATE_FIELD, ACTION_CREATE_TASK]

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'step_id': self.step_id,
            'trigger': self.trigger,
            'action_type': self.action_type,
            'action_config': self.action_config or {},
            'conditions': self.conditions,
            'delay_minutes': self.delay_minutes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<WorkflowAutomation {self.action_type} on {self.trigger}>'
