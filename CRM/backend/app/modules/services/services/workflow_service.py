"""
Workflow Service - Business Logic for Workflow Transitions

Handles workflow step transitions, validation, and state management.
"""
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.modules.services.models import ServiceRequest, RequestStateHistory
from app.modules.user.models import User, Role


class WorkflowService:
    """Service for managing workflow transitions and state"""

    DEFAULT_WORKFLOW_ID = 'default-workflow'

    @classmethod
    def get_default_workflow(cls):
        """Get the system default workflow"""
        from app.modules.services.models.workflow_models import ServiceWorkflow
        return ServiceWorkflow.query.filter_by(id=cls.DEFAULT_WORKFLOW_ID).first()

    @classmethod
    def get_workflow_for_service(cls, service):
        """Get the workflow for a given service (custom or default)"""
        from app.modules.services.models.workflow_models import ServiceWorkflow
        if service.workflow_id:
            return ServiceWorkflow.query.get(service.workflow_id)
        return cls.get_default_workflow()

    @classmethod
    def get_workflow_for_request(cls, request: ServiceRequest):
        """Get the workflow for a given service request"""
        from app.modules.services.models.workflow_models import WorkflowStep
        if request.current_step_id:
            step = WorkflowStep.query.get(request.current_step_id)
            if step:
                return step.workflow

        # Fall back to service's workflow or default
        return cls.get_workflow_for_service(request.service)

    @classmethod
    def get_current_step(cls, request: ServiceRequest):
        """Get the current workflow step for a request"""
        from app.modules.services.models.workflow_models import WorkflowStep
        if request.current_step_id:
            return WorkflowStep.query.get(request.current_step_id)

        # Map from status to step for backwards compatibility
        workflow = cls.get_workflow_for_request(request)
        if workflow:
            step = WorkflowStep.query.filter_by(
                workflow_id=workflow.id,
                name=request.status
            ).first()
            if step:
                return step

        return None

    @classmethod
    def get_available_transitions(cls, request: ServiceRequest, user: User):
        """
        Get valid next transitions for a request based on current step and user role.

        Returns list of transitions that the user can execute.
        """
        from app.modules.services.models.workflow_models import WorkflowTransition, WorkflowStep
        current_step = cls.get_current_step(request)
        if not current_step:
            return []

        # Get all outgoing transitions from current step
        transitions = WorkflowTransition.query.filter_by(
            workflow_id=current_step.workflow_id,
            from_step_id=current_step.id
        ).all()

        valid_transitions = []
        for transition in transitions:
            if cls._can_execute_transition(request, transition, user):
                # Include target step info
                to_step = WorkflowStep.query.get(transition.to_step_id)
                transition_dict = transition.to_dict()
                if to_step:
                    transition_dict['to_step'] = to_step.to_dict()
                valid_transitions.append(transition_dict)

        return valid_transitions

    @classmethod
    def _can_execute_transition(cls, request: ServiceRequest, transition, user: User):
        """Check if a user can execute a specific transition"""
        # Check role permission
        if transition.allowed_roles:
            user_role = user.role.name
            if user_role not in transition.allowed_roles:
                # Special case: request owner (user role) responding to queries
                is_owner = request.user_id == user.id
                if not (is_owner and 'user' in transition.allowed_roles):
                    return False

        # Check conditions
        if transition.requires_invoice_raised and not request.invoice_raised:
            return False

        if transition.requires_invoice_paid and not request.invoice_paid:
            return False

        if transition.requires_assignment and not request.assigned_accountant_id:
            return False

        return True

    @classmethod
    def execute_transition(cls, request: ServiceRequest, transition_id: str, user: User, notes: str = None):
        """
        Execute a workflow transition for a request.

        Returns tuple of (success, message, updated_request)
        """
        from app.modules.services.models.workflow_models import (
            WorkflowTransition, WorkflowStep, WorkflowAutomation, StepType
        )
        transition = WorkflowTransition.query.get(transition_id)
        if not transition:
            return False, 'Transition not found', None

        current_step = cls.get_current_step(request)
        if not current_step:
            return False, 'Current step not found', None

        # Verify transition is valid from current step
        if transition.from_step_id != current_step.id:
            return False, 'Invalid transition from current step', None

        # Check permissions
        if not cls._can_execute_transition(request, transition, user):
            return False, 'Not authorized to execute this transition', None

        # Get target step
        to_step = WorkflowStep.query.get(transition.to_step_id)
        if not to_step:
            return False, 'Target step not found', None

        # Track old status for history
        old_status = request.status
        old_step_id = request.current_step_id

        # Execute the transition
        request.current_step_id = to_step.id
        request.status = to_step.name  # Sync status with step name for backwards compatibility

        # Handle completed status
        if to_step.step_type == StepType.END and to_step.name == 'completed':
            request.completed_at = datetime.utcnow()

        # Record state change
        RequestStateHistory.record_state_change(
            request_id=request.id,
            from_state=old_status,
            to_state=to_step.name,
            user_id=user.id,
            notes=notes
        )

        db.session.commit()

        # Execute automations
        cls._execute_step_automations(request, to_step, 'on_enter', user)
        if old_step_id:
            old_step = WorkflowStep.query.get(old_step_id)
            if old_step:
                cls._execute_step_automations(request, old_step, 'on_exit', user)

        # Send notifications if configured
        if transition.send_notification:
            cls._send_transition_notification(request, transition, to_step, user)

        return True, 'Transition executed successfully', request

    @classmethod
    def _execute_step_automations(cls, request: ServiceRequest, step, trigger: str, user: User):
        """Execute automations for a step"""
        from app.modules.services.models.workflow_models import WorkflowAutomation
        from app.modules.services.services.workflow_automation import WorkflowAutomationExecutor

        automations = WorkflowAutomation.query.filter_by(
            step_id=step.id,
            trigger=trigger,
            is_active=True
        ).all()

        for automation in automations:
            try:
                WorkflowAutomationExecutor.execute(automation, request, user)
            except Exception as e:
                current_app.logger.error(f'Failed to execute automation {automation.id}: {str(e)}')

    @classmethod
    def _send_transition_notification(cls, request: ServiceRequest, transition,
                                       to_step, user: User):
        """Send notification about a transition"""
        from app.modules.services.models.workflow_models import WorkflowStep
        try:
            from app.modules.notifications.services import NotificationService

            # Determine who to notify based on step configuration
            recipients = []

            # Notify client if step has notify_client
            if to_step.notify_client:
                client = User.query.get(request.user_id)
                if client:
                    recipients.append(client)

            # Notify roles specified in step
            if to_step.notify_roles:
                for role_name in to_step.notify_roles:
                    role = Role.query.filter_by(name=role_name).first()
                    if role:
                        # Get users with this role in the same company
                        request_user = User.query.get(request.user_id)
                        if request_user and request_user.company_id:
                            users = User.query.filter(
                                User.role_id == role.id,
                                User.company_id == request_user.company_id,
                                User.is_active == True
                            ).all()
                            recipients.extend(users)

            # Notify assigned accountant
            if request.assigned_accountant_id:
                accountant = User.query.get(request.assigned_accountant_id)
                if accountant and accountant not in recipients:
                    recipients.append(accountant)

            # Remove duplicates and send
            seen_ids = set()
            unique_recipients = []
            for r in recipients:
                if r.id not in seen_ids and r.id != user.id:  # Don't notify the user who triggered
                    seen_ids.add(r.id)
                    unique_recipients.append(r)

            if unique_recipients:
                NotificationService.send_workflow_transition_notification(
                    request=request,
                    recipients=unique_recipients,
                    transition_name=transition.name or 'Status Update',
                    new_status=to_step.display_name or to_step.name,
                    triggered_by=user
                )

        except Exception as e:
            current_app.logger.error(f'Failed to send transition notification: {str(e)}')

    @classmethod
    def initialize_request_workflow(cls, request: ServiceRequest):
        """Initialize a new request with the appropriate workflow start step"""
        workflow = cls.get_workflow_for_service(request.service)
        if not workflow:
            workflow = cls.get_default_workflow()

        if workflow:
            start_step = workflow.get_start_step()
            if start_step:
                request.current_step_id = start_step.id
                request.status = start_step.name

        return request

    @classmethod
    def validate_workflow(cls, workflow):
        """
        Validate a workflow configuration.

        Returns tuple of (is_valid, errors)
        """
        from app.modules.services.models.workflow_models import StepType
        errors = []

        steps = workflow.steps.all()
        if not steps:
            errors.append('Workflow must have at least one step')
            return False, errors

        # Check for START step
        start_steps = [s for s in steps if s.step_type == StepType.START]
        if len(start_steps) == 0:
            errors.append('Workflow must have exactly one START step')
        elif len(start_steps) > 1:
            errors.append('Workflow cannot have multiple START steps')

        # Check for END step
        end_steps = [s for s in steps if s.step_type == StepType.END]
        if len(end_steps) == 0:
            errors.append('Workflow must have at least one END step')

        # Check all steps are reachable
        transitions = workflow.transitions.all()
        reachable = set()

        if start_steps:
            reachable.add(start_steps[0].id)
            changed = True
            while changed:
                changed = False
                for t in transitions:
                    if t.from_step_id in reachable and t.to_step_id not in reachable:
                        reachable.add(t.to_step_id)
                        changed = True

        unreachable = [s for s in steps if s.id not in reachable and s.step_type != StepType.START]
        if unreachable:
            names = [s.display_name or s.name for s in unreachable]
            errors.append(f'Some steps are unreachable: {", ".join(names)}')

        # Check END steps are reachable
        for end_step in end_steps:
            if end_step.id not in reachable:
                errors.append(f'END step "{end_step.display_name or end_step.name}" is not reachable')

        return len(errors) == 0, errors

    @classmethod
    def duplicate_workflow(cls, workflow, new_name: str, company_id: str = None,
                           created_by_id: str = None):
        """
        Create a copy of a workflow.

        Returns the new workflow.
        """
        import uuid
        from app.modules.services.models.workflow_models import (
            ServiceWorkflow, WorkflowStep, WorkflowTransition, WorkflowAutomation
        )

        # Create new workflow
        new_workflow = ServiceWorkflow(
            id=str(uuid.uuid4()),
            company_id=company_id,
            name=new_name,
            description=workflow.description,
            is_default=False,
            is_active=True,
            created_by_id=created_by_id
        )
        db.session.add(new_workflow)
        db.session.flush()

        # Map old step IDs to new step IDs
        step_id_map = {}

        # Copy steps
        for old_step in workflow.steps.order_by(WorkflowStep.order).all():
            new_step = WorkflowStep(
                id=str(uuid.uuid4()),
                workflow_id=new_workflow.id,
                name=old_step.name,
                display_name=old_step.display_name,
                description=old_step.description,
                color=old_step.color,
                icon=old_step.icon,
                step_type=old_step.step_type,
                order=old_step.order,
                allowed_roles=old_step.allowed_roles,
                required_fields=old_step.required_fields,
                auto_assign=old_step.auto_assign,
                notify_roles=old_step.notify_roles,
                notify_client=old_step.notify_client,
                position_x=old_step.position_x,
                position_y=old_step.position_y
            )
            db.session.add(new_step)
            step_id_map[old_step.id] = new_step.id

        db.session.flush()

        # Copy transitions with updated step IDs
        for old_transition in workflow.transitions.all():
            new_transition = WorkflowTransition(
                id=str(uuid.uuid4()),
                workflow_id=new_workflow.id,
                from_step_id=step_id_map[old_transition.from_step_id],
                to_step_id=step_id_map[old_transition.to_step_id],
                name=old_transition.name,
                description=old_transition.description,
                requires_invoice_raised=old_transition.requires_invoice_raised,
                requires_invoice_paid=old_transition.requires_invoice_paid,
                requires_assignment=old_transition.requires_assignment,
                allowed_roles=old_transition.allowed_roles,
                send_notification=old_transition.send_notification,
                notification_template=old_transition.notification_template
            )
            db.session.add(new_transition)

        # Copy automations with updated step IDs
        for old_automation in workflow.automations.all():
            new_step_id = step_id_map.get(old_automation.step_id) if old_automation.step_id else None
            new_automation = WorkflowAutomation(
                id=str(uuid.uuid4()),
                workflow_id=new_workflow.id,
                step_id=new_step_id,
                trigger=old_automation.trigger,
                action_type=old_automation.action_type,
                action_config=old_automation.action_config,
                conditions=old_automation.conditions,
                delay_minutes=old_automation.delay_minutes,
                is_active=old_automation.is_active
            )
            db.session.add(new_automation)

        db.session.commit()
        return new_workflow
