"""
Task Routes
===========
API endpoints for task management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.modules.services.models.task import Task
from app.modules.user.models import User
from app.common.decorators import admin_required, accountant_required
from app.modules.services.services.status_resolver import StatusResolver

# Create blueprint
task_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def get_current_user():
    """Get the current authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def error_response(message: str, status_code: int = 400):
    """Create an error response."""
    return jsonify({'success': False, 'error': message}), status_code


def success_response(data: dict, status_code: int = 200):
    """Create a success response."""
    return jsonify({'success': True, 'data': data}), status_code


# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@task_bp.route('', methods=['GET'])
@jwt_required()
@accountant_required
def list_tasks():
    """
    List tasks.
    - Admins/Senior Accountants: See all tasks in company
    - Accountants: See only tasks assigned to them

    Query params:
        - status: Filter by status (todo, in_progress, review, done)
        - priority: Filter by priority (low, normal, high, urgent)
        - assigned_to_id: Filter by assignee (admin only)
        - service_request_id: Filter by linked request
        - standalone: If 'true', only show tasks not linked to requests
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    # Base query - filter by company
    query = Task.query.filter_by(company_id=current_user.company_id)

    # Accountants can only see their assigned tasks
    if current_user.role.name == 'accountant':
        query = query.filter_by(assigned_to_id=current_user.id)
    elif current_user.role.name == 'external_accountant':
        query = query.filter_by(assigned_to_id=current_user.id)

    # Apply filters
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)

    assigned_to_id = request.args.get('assigned_to_id')
    if assigned_to_id and current_user.role.name in ['super_admin', 'admin', 'senior_accountant']:
        query = query.filter_by(assigned_to_id=assigned_to_id)

    service_request_id = request.args.get('service_request_id')
    if service_request_id:
        query = query.filter_by(service_request_id=service_request_id)

    standalone = request.args.get('standalone')
    if standalone == 'true':
        query = query.filter(Task.service_request_id.is_(None))

    # Order by due date (nulls last), then by created_at
    tasks = query.order_by(
        Task.due_date.asc().nullslast(),
        Task.created_at.desc()
    ).all()

    return success_response([task.to_dict() for task in tasks])


@task_bp.route('', methods=['POST'])
@jwt_required()
@accountant_required
def create_task():
    """
    Create a new task.

    All staff can create tasks (like DevOps story board):
    - Accountants: Can create tasks and assign to themselves only
    - Admins/Senior Accountants: Can create tasks and assign to anyone

    Body:
        - title: Task title (required)
        - description: Task description
        - assigned_to_id: User ID to assign the task to
        - service_request_id: Link to a service request (optional)
        - priority: low, normal, high, urgent (default: normal)
        - due_date: Due date (YYYY-MM-DD)
        - estimated_minutes: Estimated time in minutes
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    data = request.json or {}
    is_admin = current_user.role.name in ['super_admin', 'admin', 'senior_accountant']

    # Validate required fields
    if not data.get('title'):
        return error_response('Title is required', 400)

    # Validate priority
    priority = data.get('priority', 'normal')
    if priority not in Task.VALID_PRIORITIES:
        return error_response(f'Invalid priority. Must be one of: {", ".join(Task.VALID_PRIORITIES)}', 400)

    # Handle assignment
    assigned_to_id = data.get('assigned_to_id')

    # Accountants can only assign tasks to themselves
    if not is_admin:
        if assigned_to_id and assigned_to_id != current_user.id:
            return error_response('You can only assign tasks to yourself', 403)
        # Auto-assign to self if not specified
        if not assigned_to_id:
            assigned_to_id = current_user.id

    # Validate assigned user belongs to same company
    if assigned_to_id:
        assigned_user = User.query.get(assigned_to_id)
        if not assigned_user or assigned_user.company_id != current_user.company_id:
            return error_response('Invalid assignee', 400)

    # Parse due date
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid due_date format. Use YYYY-MM-DD', 400)

    # Create task
    task = Task(
        company_id=current_user.company_id,
        title=data['title'],
        description=data.get('description'),
        created_by_id=current_user.id,
        assigned_to_id=assigned_to_id or None,
        service_request_id=data.get('service_request_id') or None,
        priority=priority,
        due_date=due_date,
        estimated_minutes=data.get('estimated_minutes'),
        status=Task.STATUS_PENDING
    )

    db.session.add(task)
    db.session.commit()

    # TODO: Send notification to assigned user

    return success_response(task.to_dict(), 201)


@task_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_task(task_id):
    """
    Get a single task by ID.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    # Check permission
    if task.company_id != current_user.company_id:
        return error_response('Task not found', 404)

    # Accountants can only view their own tasks
    if current_user.role.name in ['accountant', 'external_accountant']:
        if task.assigned_to_id != current_user.id:
            return error_response('Access denied', 403)

    return success_response(task.to_dict())


@task_bp.route('/<task_id>', methods=['PATCH'])
@jwt_required()
@accountant_required
def update_task(task_id):
    """
    Update a task.

    - Assignees can update: status, actual_minutes
    - Admins/Senior Accountants can update all fields

    Body (all optional):
        - title: Task title
        - description: Task description
        - assigned_to_id: User ID to assign the task to
        - service_request_id: Link to a service request
        - status: todo, in_progress, review, done
        - priority: low, normal, high, urgent
        - due_date: Due date (YYYY-MM-DD)
        - estimated_minutes: Estimated time in minutes
        - actual_minutes: Actual time spent in minutes
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    # Check permission
    if task.company_id != current_user.company_id:
        return error_response('Task not found', 404)

    data = request.json or {}

    # Determine permission level
    is_admin = current_user.role.name in ['super_admin', 'admin', 'senior_accountant']
    is_assignee = task.assigned_to_id == current_user.id
    is_creator = task.created_by_id == current_user.id

    if not (is_admin or is_assignee or is_creator):
        return error_response('Access denied', 403)

    # Assignee-only fields
    assignee_fields = ['status', 'actual_minutes']
    # Admin-only fields
    admin_fields = ['title', 'description', 'assigned_to_id', 'service_request_id', 'priority', 'due_date', 'estimated_minutes']

    # Update status
    if 'status' in data:
        new_status = data['status']
        valid_keys = StatusResolver.get_valid_keys(current_user.company_id, 'task')
        if new_status not in valid_keys:
            return error_response(f'Invalid status. Must be one of: {", ".join(valid_keys)}', 400)
        task.status = new_status
        # Set completed_at when marking as final
        if StatusResolver.is_final_status(current_user.company_id, new_status):
            task.completed_at = datetime.utcnow()
        elif task.completed_at and not StatusResolver.is_final_status(current_user.company_id, new_status):
            task.completed_at = None

    # Update actual_minutes
    if 'actual_minutes' in data:
        task.actual_minutes = data['actual_minutes']

    # Admin-only updates
    if is_admin:
        if 'title' in data:
            if not data['title']:
                return error_response('Title cannot be empty', 400)
            task.title = data['title']

        if 'description' in data:
            task.description = data['description']

        if 'assigned_to_id' in data:
            assigned_to_id = data['assigned_to_id']
            if assigned_to_id:
                assigned_user = User.query.get(assigned_to_id)
                if not assigned_user or assigned_user.company_id != current_user.company_id:
                    return error_response('Invalid assignee', 400)
            task.assigned_to_id = assigned_to_id or None

        if 'service_request_id' in data:
            task.service_request_id = data['service_request_id'] or None

        if 'priority' in data:
            if data['priority'] not in Task.VALID_PRIORITIES:
                return error_response(f'Invalid priority. Must be one of: {", ".join(Task.VALID_PRIORITIES)}', 400)
            task.priority = data['priority']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                except ValueError:
                    return error_response('Invalid due_date format. Use YYYY-MM-DD', 400)
            else:
                task.due_date = None

        if 'estimated_minutes' in data:
            task.estimated_minutes = data['estimated_minutes']

    db.session.commit()

    return success_response(task.to_dict())


@task_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_task(task_id):
    """
    Delete a task.

    Admin/Senior Accountant only.
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    # Check permission
    if task.company_id != current_user.company_id:
        return error_response('Task not found', 404)

    db.session.delete(task)
    db.session.commit()

    return success_response({'message': 'Task deleted successfully'})


@task_bp.route('/<task_id>/status', methods=['PATCH'])
@jwt_required()
@accountant_required
def update_task_status(task_id):
    """
    Quick endpoint to update just the task status (for Kanban drag-drop).

    Body:
        - status: todo, in_progress, review, done
    """
    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 404)

    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    # Check permission
    if task.company_id != current_user.company_id:
        return error_response('Task not found', 404)

    # Accountants can only update their own tasks
    if current_user.role.name in ['accountant', 'external_accountant']:
        if task.assigned_to_id != current_user.id:
            return error_response('Access denied', 403)

    data = request.json or {}
    new_status = data.get('status')

    if not new_status:
        return error_response('Status is required', 400)

    valid_keys = StatusResolver.get_valid_keys(current_user.company_id, 'task')
    if new_status not in valid_keys:
        return error_response(f'Invalid status. Must be one of: {", ".join(valid_keys)}', 400)

    task.status = new_status

    # Set completed_at when marking as final
    if StatusResolver.is_final_status(current_user.company_id, new_status):
        task.completed_at = datetime.utcnow()
    elif task.completed_at and not StatusResolver.is_final_status(current_user.company_id, new_status):
        task.completed_at = None

    db.session.commit()

    return success_response(task.to_dict())
