"""
Workflow API Routes

CRUD endpoints for managing service workflows, steps, and transitions.
"""
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.modules.services.models.workflow_models import (
    ServiceWorkflow, WorkflowStep, WorkflowTransition, WorkflowAutomation, StepType
)
from app.modules.services.services.workflow_service import WorkflowService
from app.modules.services.models import ServiceRequest
from app.modules.user.models import User, Role

workflow_bp = Blueprint('workflows', __name__)


def get_current_user():
    """Get the current authenticated user"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def require_admin():
    """Check if current user is admin or super_admin"""
    user = get_current_user()
    if not user or user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    return None


# ============== Workflow CRUD ==============

@workflow_bp.route('', methods=['GET'])
@jwt_required()
def list_workflows():
    """List all workflows for the user's company (or all for super admin)"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    query = ServiceWorkflow.query

    if user.role.name == Role.SUPER_ADMIN:
        # Super admin can see all workflows
        company_id = request.args.get('company_id')
        if company_id:
            query = query.filter(
                db.or_(ServiceWorkflow.company_id == company_id, ServiceWorkflow.is_default == True)
            )
    else:
        # Admin/accountant can only see their company's workflows + default
        query = query.filter(
            db.or_(
                ServiceWorkflow.company_id == user.company_id,
                ServiceWorkflow.is_default == True
            )
        )

    # Filter by active status
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    if active_only:
        query = query.filter(ServiceWorkflow.is_active == True)

    workflows = query.order_by(ServiceWorkflow.is_default.desc(), ServiceWorkflow.name).all()

    return jsonify({
        'success': True,
        'data': {
            'workflows': [w.to_dict(include_steps=False, include_transitions=False) for w in workflows]
        }
    })


@workflow_bp.route('/<workflow_id>', methods=['GET'])
@jwt_required()
def get_workflow(workflow_id):
    """Get a workflow with all steps and transitions"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    workflow = ServiceWorkflow.query.get(workflow_id)
    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Check access
    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id and workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    return jsonify({
        'success': True,
        'data': {
            'workflow': workflow.to_dict(include_steps=True, include_transitions=True)
        }
    })


@workflow_bp.route('', methods=['POST'])
@jwt_required()
def create_workflow():
    """Create a new workflow"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'success': False, 'error': 'Workflow name is required'}), 400

    # Determine company_id
    if user.role.name == Role.SUPER_ADMIN:
        company_id = data.get('company_id')  # Super admin can specify company
    else:
        company_id = user.company_id

    workflow = ServiceWorkflow(
        id=str(uuid.uuid4()),
        company_id=company_id,
        name=data['name'],
        description=data.get('description'),
        is_default=False,
        is_active=True,
        created_by_id=user.id
    )

    db.session.add(workflow)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'workflow': workflow.to_dict()
        }
    }), 201


@workflow_bp.route('/<workflow_id>', methods=['PUT'])
@jwt_required()
def update_workflow(workflow_id):
    """Update a workflow"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    workflow = ServiceWorkflow.query.get(workflow_id)

    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if 'name' in data:
        workflow.name = data['name']
    if 'description' in data:
        workflow.description = data['description']
    if 'is_active' in data:
        workflow.is_active = data['is_active']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'workflow': workflow.to_dict()
        }
    })


@workflow_bp.route('/<workflow_id>', methods=['DELETE'])
@jwt_required()
def delete_workflow(workflow_id):
    """Delete a workflow (if not in use)"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    workflow = ServiceWorkflow.query.get(workflow_id)

    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Cannot delete default workflow
    if workflow.is_default:
        return jsonify({'success': False, 'error': 'Cannot delete default workflow'}), 403

    # Check access
    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    # Check if workflow is in use
    from app.modules.services.models import Service
    services_using = Service.query.filter_by(workflow_id=workflow_id).count()
    if services_using > 0:
        return jsonify({
            'success': False,
            'error': f'Workflow is used by {services_using} service(s). Remove workflow from services first.'
        }), 400

    db.session.delete(workflow)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Workflow deleted successfully'
    })


@workflow_bp.route('/<workflow_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_workflow(workflow_id):
    """Duplicate a workflow"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    workflow = ServiceWorkflow.query.get(workflow_id)

    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    data = request.get_json()
    new_name = data.get('name', f'{workflow.name} (Copy)')

    # Determine company_id for the copy
    if user.role.name == Role.SUPER_ADMIN:
        company_id = data.get('company_id') or workflow.company_id
    else:
        company_id = user.company_id

    new_workflow = WorkflowService.duplicate_workflow(
        workflow=workflow,
        new_name=new_name,
        company_id=company_id,
        created_by_id=user.id
    )

    return jsonify({
        'success': True,
        'data': {
            'workflow': new_workflow.to_dict()
        }
    }), 201


@workflow_bp.route('/<workflow_id>/validate', methods=['GET'])
@jwt_required()
def validate_workflow(workflow_id):
    """Validate a workflow configuration"""
    workflow = ServiceWorkflow.query.get(workflow_id)
    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    is_valid, errors = WorkflowService.validate_workflow(workflow)

    return jsonify({
        'success': True,
        'data': {
            'is_valid': is_valid,
            'errors': errors
        }
    })


# ============== Step CRUD ==============

@workflow_bp.route('/<workflow_id>/steps', methods=['POST'])
@jwt_required()
def add_step(workflow_id):
    """Add a step to a workflow"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    workflow = ServiceWorkflow.query.get(workflow_id)

    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if not data.get('name'):
        return jsonify({'success': False, 'error': 'Step name is required'}), 400

    # Get max order
    max_order = db.session.query(db.func.max(WorkflowStep.order)).filter_by(workflow_id=workflow_id).scalar() or 0

    # Parse step type
    step_type_str = data.get('step_type', 'NORMAL')
    try:
        step_type = StepType[step_type_str]
    except KeyError:
        return jsonify({'success': False, 'error': f'Invalid step type: {step_type_str}'}), 400

    step = WorkflowStep(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        name=data['name'],
        display_name=data.get('display_name'),
        description=data.get('description'),
        color=data.get('color', 'blue'),
        icon=data.get('icon'),
        step_type=step_type,
        order=data.get('order', max_order + 1),
        allowed_roles=data.get('allowed_roles'),
        required_fields=data.get('required_fields'),
        auto_assign=data.get('auto_assign', False),
        notify_roles=data.get('notify_roles'),
        notify_client=data.get('notify_client', False),
        position_x=data.get('position_x', 0),
        position_y=data.get('position_y', 0)
    )

    db.session.add(step)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'step': step.to_dict()
        }
    }), 201


@workflow_bp.route('/<workflow_id>/steps/<step_id>', methods=['PUT'])
@jwt_required()
def update_step(workflow_id, step_id):
    """Update a workflow step"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    step = WorkflowStep.query.get(step_id)

    if not step or step.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Step not found'}), 404

    workflow = step.workflow

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if 'name' in data:
        step.name = data['name']
    if 'display_name' in data:
        step.display_name = data['display_name']
    if 'description' in data:
        step.description = data['description']
    if 'color' in data:
        step.color = data['color']
    if 'icon' in data:
        step.icon = data['icon']
    if 'step_type' in data:
        try:
            step.step_type = StepType[data['step_type']]
        except KeyError:
            return jsonify({'success': False, 'error': f'Invalid step type: {data["step_type"]}'}), 400
    if 'order' in data:
        step.order = data['order']
    if 'allowed_roles' in data:
        step.allowed_roles = data['allowed_roles']
    if 'required_fields' in data:
        step.required_fields = data['required_fields']
    if 'auto_assign' in data:
        step.auto_assign = data['auto_assign']
    if 'notify_roles' in data:
        step.notify_roles = data['notify_roles']
    if 'notify_client' in data:
        step.notify_client = data['notify_client']
    if 'position_x' in data:
        step.position_x = data['position_x']
    if 'position_y' in data:
        step.position_y = data['position_y']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'step': step.to_dict()
        }
    })


@workflow_bp.route('/<workflow_id>/steps/<step_id>', methods=['DELETE'])
@jwt_required()
def delete_step(workflow_id, step_id):
    """Remove a step from a workflow"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    step = WorkflowStep.query.get(step_id)

    if not step or step.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Step not found'}), 404

    workflow = step.workflow

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    # Check if any requests are on this step
    requests_on_step = ServiceRequest.query.filter_by(current_step_id=step_id).count()
    if requests_on_step > 0:
        return jsonify({
            'success': False,
            'error': f'{requests_on_step} request(s) are currently on this step. Move them first.'
        }), 400

    db.session.delete(step)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Step deleted successfully'
    })


# ============== Transition CRUD ==============

@workflow_bp.route('/<workflow_id>/transitions', methods=['POST'])
@jwt_required()
def add_transition(workflow_id):
    """Add a transition between steps"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    workflow = ServiceWorkflow.query.get(workflow_id)

    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if not data.get('from_step_id') or not data.get('to_step_id'):
        return jsonify({'success': False, 'error': 'from_step_id and to_step_id are required'}), 400

    # Verify steps exist and belong to this workflow
    from_step = WorkflowStep.query.get(data['from_step_id'])
    to_step = WorkflowStep.query.get(data['to_step_id'])

    if not from_step or from_step.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Invalid from_step_id'}), 400
    if not to_step or to_step.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Invalid to_step_id'}), 400

    # Check for duplicate transition
    existing = WorkflowTransition.query.filter_by(
        workflow_id=workflow_id,
        from_step_id=data['from_step_id'],
        to_step_id=data['to_step_id']
    ).first()

    if existing:
        return jsonify({'success': False, 'error': 'Transition already exists'}), 400

    transition = WorkflowTransition(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        from_step_id=data['from_step_id'],
        to_step_id=data['to_step_id'],
        name=data.get('name'),
        description=data.get('description'),
        requires_invoice_raised=data.get('requires_invoice_raised', False),
        requires_invoice_paid=data.get('requires_invoice_paid', False),
        requires_assignment=data.get('requires_assignment', False),
        allowed_roles=data.get('allowed_roles'),
        send_notification=data.get('send_notification', True),
        notification_template=data.get('notification_template')
    )

    db.session.add(transition)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'transition': transition.to_dict()
        }
    }), 201


@workflow_bp.route('/<workflow_id>/transitions/<transition_id>', methods=['PUT'])
@jwt_required()
def update_transition(workflow_id, transition_id):
    """Update a transition"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    transition = WorkflowTransition.query.get(transition_id)

    if not transition or transition.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Transition not found'}), 404

    workflow = transition.workflow

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if 'name' in data:
        transition.name = data['name']
    if 'description' in data:
        transition.description = data['description']
    if 'requires_invoice_raised' in data:
        transition.requires_invoice_raised = data['requires_invoice_raised']
    if 'requires_invoice_paid' in data:
        transition.requires_invoice_paid = data['requires_invoice_paid']
    if 'requires_assignment' in data:
        transition.requires_assignment = data['requires_assignment']
    if 'allowed_roles' in data:
        transition.allowed_roles = data['allowed_roles']
    if 'send_notification' in data:
        transition.send_notification = data['send_notification']
    if 'notification_template' in data:
        transition.notification_template = data['notification_template']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'transition': transition.to_dict()
        }
    })


@workflow_bp.route('/<workflow_id>/transitions/<transition_id>', methods=['DELETE'])
@jwt_required()
def delete_transition(workflow_id, transition_id):
    """Remove a transition"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    transition = WorkflowTransition.query.get(transition_id)

    if not transition or transition.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Transition not found'}), 404

    workflow = transition.workflow

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    db.session.delete(transition)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Transition deleted successfully'
    })


# ============== Automation CRUD ==============

@workflow_bp.route('/<workflow_id>/automations', methods=['GET'])
@jwt_required()
def list_automations(workflow_id):
    """List all automations for a workflow"""
    workflow = ServiceWorkflow.query.get(workflow_id)
    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    automations = WorkflowAutomation.query.filter_by(workflow_id=workflow_id).all()

    return jsonify({
        'success': True,
        'data': {
            'automations': [a.to_dict() for a in automations]
        }
    })


@workflow_bp.route('/<workflow_id>/automations', methods=['POST'])
@jwt_required()
def add_automation(workflow_id):
    """Add an automation rule to a workflow"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    workflow = ServiceWorkflow.query.get(workflow_id)

    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if not data.get('trigger'):
        return jsonify({'success': False, 'error': 'Trigger type is required'}), 400
    if not data.get('action_type'):
        return jsonify({'success': False, 'error': 'Action type is required'}), 400

    # Validate trigger
    if data['trigger'] not in WorkflowAutomation.VALID_TRIGGERS:
        return jsonify({'success': False, 'error': f'Invalid trigger: {data["trigger"]}'}), 400

    # Validate action type
    if data['action_type'] not in WorkflowAutomation.VALID_ACTIONS:
        return jsonify({'success': False, 'error': f'Invalid action type: {data["action_type"]}'}), 400

    automation = WorkflowAutomation(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        step_id=data.get('step_id'),
        trigger=data['trigger'],
        action_type=data['action_type'],
        action_config=data.get('action_config'),
        conditions=data.get('conditions'),
        delay_minutes=data.get('delay_minutes'),
        is_active=data.get('is_active', True)
    )

    db.session.add(automation)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'automation': automation.to_dict()
        }
    }), 201


@workflow_bp.route('/<workflow_id>/automations/<automation_id>', methods=['PUT'])
@jwt_required()
def update_automation(workflow_id, automation_id):
    """Update an automation rule"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    automation = WorkflowAutomation.query.get(automation_id)

    if not automation or automation.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Automation not found'}), 404

    workflow = automation.workflow

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if 'step_id' in data:
        automation.step_id = data['step_id']
    if 'trigger' in data:
        if data['trigger'] not in WorkflowAutomation.VALID_TRIGGERS:
            return jsonify({'success': False, 'error': f'Invalid trigger: {data["trigger"]}'}), 400
        automation.trigger = data['trigger']
    if 'action_type' in data:
        if data['action_type'] not in WorkflowAutomation.VALID_ACTIONS:
            return jsonify({'success': False, 'error': f'Invalid action type: {data["action_type"]}'}), 400
        automation.action_type = data['action_type']
    if 'action_config' in data:
        automation.action_config = data['action_config']
    if 'conditions' in data:
        automation.conditions = data['conditions']
    if 'delay_minutes' in data:
        automation.delay_minutes = data['delay_minutes']
    if 'is_active' in data:
        automation.is_active = data['is_active']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'automation': automation.to_dict()
        }
    })


@workflow_bp.route('/<workflow_id>/automations/<automation_id>', methods=['DELETE'])
@jwt_required()
def delete_automation(workflow_id, automation_id):
    """Delete an automation rule"""
    error = require_admin()
    if error:
        return error

    user = get_current_user()
    automation = WorkflowAutomation.query.get(automation_id)

    if not automation or automation.workflow_id != workflow_id:
        return jsonify({'success': False, 'error': 'Automation not found'}), 404

    workflow = automation.workflow

    # Check access
    if workflow.is_default and user.role.name != Role.SUPER_ADMIN:
        return jsonify({'success': False, 'error': 'Cannot modify default workflow'}), 403

    if user.role.name != Role.SUPER_ADMIN:
        if workflow.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403

    db.session.delete(automation)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Automation deleted successfully'
    })


# ============== Request Workflow Operations ==============

@workflow_bp.route('/requests/<request_id>/transitions', methods=['GET'])
@jwt_required()
def get_request_transitions(request_id):
    """Get available transitions for a service request"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return jsonify({'success': False, 'error': 'Request not found'}), 404

    # Check access
    from app.modules.services.repositories import ServiceRequestRepository
    repo = ServiceRequestRepository()

    is_owner = service_request.user_id == user.id
    can_access = repo.can_user_access_request(user, service_request)

    if not can_access and not is_owner:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    # Get available transitions
    transitions = WorkflowService.get_available_transitions(service_request, user)

    # Get current step info
    current_step = WorkflowService.get_current_step(service_request)
    current_step_data = current_step.to_dict() if current_step else None

    return jsonify({
        'success': True,
        'data': {
            'current_step': current_step_data,
            'available_transitions': transitions
        }
    })


@workflow_bp.route('/requests/<request_id>/transitions/<transition_id>', methods=['POST'])
@jwt_required()
def execute_request_transition(request_id, transition_id):
    """Execute a workflow transition on a service request"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return jsonify({'success': False, 'error': 'Request not found'}), 404

    # Check access
    from app.modules.services.repositories import ServiceRequestRepository
    repo = ServiceRequestRepository()

    is_owner = service_request.user_id == user.id
    can_access = repo.can_user_access_request(user, service_request)

    if not can_access and not is_owner:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json() or {}
    notes = data.get('notes')

    # Execute the transition
    success, message, updated_request = WorkflowService.execute_transition(
        request=service_request,
        transition_id=transition_id,
        user=user,
        notes=notes
    )

    if not success:
        return jsonify({'success': False, 'error': message}), 400

    return jsonify({
        'success': True,
        'message': message,
        'data': {
            'request': updated_request.to_dict(include_notes=True)
        }
    })


@workflow_bp.route('/requests/<request_id>/workflow', methods=['GET'])
@jwt_required()
def get_request_workflow(request_id):
    """Get the complete workflow for a request (for visualization)"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return jsonify({'success': False, 'error': 'Request not found'}), 404

    # Get workflow
    workflow = WorkflowService.get_workflow_for_request(service_request)
    if not workflow:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    # Get current step
    current_step = WorkflowService.get_current_step(service_request)

    return jsonify({
        'success': True,
        'data': {
            'workflow': workflow.to_dict(include_steps=True, include_transitions=True),
            'current_step_id': current_step.id if current_step else None
        }
    })
