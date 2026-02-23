"""
Forms Routes - API Endpoints
============================

This module provides HTTP endpoints for dynamic form management.
Forms can be customized per company with various question types.

Features:
---------
- System forms (default templates) vs Company-specific forms
- Form cloning for easy customization
- Multiple question types (text, select, file upload, etc.)
- Form versioning with draft/published/archived statuses
- Form responses linked to service requests

Endpoints:
---------
Form CRUD:
    GET    /forms/              - List all forms
    POST   /forms/              - Create form (Super Admin)
    GET    /forms/<id>          - Get form by ID
    PATCH  /forms/<id>          - Update form
    DELETE /forms/<id>          - Delete form

Company Forms:
    GET    /forms/defaults      - List default forms for cloning
    POST   /forms/<id>/clone    - Clone form for company
    GET    /forms/company       - List company's forms
    POST   /forms/company       - Create company form
    PATCH  /forms/<id>/status   - Update form status

Questions:
    POST   /forms/<id>/questions     - Add question
    PATCH  /forms/questions/<id>     - Update question
    DELETE /forms/questions/<id>     - Delete question
    POST   /forms/<id>/reorder       - Reorder questions

Responses:
    POST   /forms/<id>/submit        - Submit form response
    GET    /forms/<id>/responses     - List responses
    GET    /forms/responses/<id>     - Get single response
    PATCH  /forms/responses/<id>     - Update response

Author: CRM Development Team
"""

import logging
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError

# Configure module-level logger
logger = logging.getLogger(__name__)

from app.modules.forms import forms_bp
from app.modules.forms.usecases import (
    CreateFormUseCase,
    UpdateFormUseCase,
    DeleteFormUseCase,
    GetFormUseCase,
    ListFormsUseCase,
    AddQuestionUseCase,
    UpdateQuestionUseCase,
    DeleteQuestionUseCase,
    ReorderQuestionsUseCase,
    SubmitFormResponseUseCase,
    GetFormResponseUseCase,
    ListFormResponsesUseCase,
    ListDefaultFormsUseCase,
    CloneFormUseCase,
    CreateCompanyFormUseCase,
    UpdateFormStatusUseCase,
    ListCompanyFormsUseCase,
    DeleteCompanyFormUseCase
)
from app.modules.forms.schemas import (
    CreateFormSchema, UpdateFormSchema, AddQuestionSchema,
    UpdateQuestionSchema, SubmitResponseSchema, CloneFormSchema,
    UpdateFormStatusSchema
)
from app.common.decorators import roles_required, get_current_user, admin_required
from app.common.responses import success_response, error_response


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'INVALID_TYPE': 400,
        'REQUIRED_FIELD': 400,
        'FORBIDDEN': 403
    }
    return status_map.get(error_code, 400)


# ============== Form CRUD ==============

@forms_bp.route('/', methods=['GET'])
@jwt_required()
def list_forms():
    """List all forms"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    form_type = request.args.get('type')
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    usecase = ListFormsUseCase()
    result = usecase.execute(form_type, active_only, page, per_page)

    return success_response(result.data)


@forms_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_form():
    """Create a new form (Admin or Super Admin)"""
    try:
        schema = CreateFormSchema()
        data = schema.load(request.get_json(silent=True) or {})
        user_id = get_jwt_identity()

        usecase = CreateFormUseCase()
        result = usecase.execute(
            name=data['name'],
            form_type=data['form_type'],
            created_by_id=user_id,
            description=data.get('description'),
            questions=data.get('questions')
        )

        if result.success:
            return success_response(
                result.data,
                message='Form created successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/<int:form_id>', methods=['GET'])
@jwt_required()
def get_form(form_id):
    """Get a form by ID"""
    usecase = GetFormUseCase()
    result = usecase.execute(form_id)

    if result.success:
        return success_response(result.data)
    else:
        return error_response(result.error, _get_status_code(result.error_code))


@forms_bp.route('/<int:form_id>', methods=['PATCH', 'PUT'])
@jwt_required()
@admin_required
def update_form(form_id):
    """Update a form (Admin can update company forms, Super Admin can update any)"""
    try:
        # Verify access to form
        current_user = get_current_user()
        from app.modules.forms.models import Form
        form = Form.query.get(form_id)
        if not form:
            return error_response('Form not found', 404)

        # Check access: Super Admin can edit any, Admin can edit company forms only
        if current_user.role.name != 'super_admin':
            if form.company_id != current_user.company_id:
                return error_response('Access denied to this form', 403)

        schema = UpdateFormSchema()
        data = schema.load(request.get_json(silent=True) or {})

        usecase = UpdateFormUseCase()
        result = usecase.execute(form_id, data)

        if result.success:
            return success_response(
                result.data,
                message='Form updated successfully'
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/<int:form_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_form(form_id):
    """Delete a form (Admin can delete company forms, Super Admin can delete any)"""
    user_id = get_jwt_identity()

    usecase = DeleteCompanyFormUseCase()
    result = usecase.execute(form_id, user_id)

    if result.success:
        return success_response(message='Form deleted successfully')
    else:
        return error_response(result.error, _get_status_code(result.error_code))


# ============== Company Form Management ==============

@forms_bp.route('/defaults', methods=['GET'])
@jwt_required()
def list_default_forms():
    """List all default/system forms available for cloning"""
    include_questions = request.args.get('include_questions', 'false').lower() == 'true'

    usecase = ListDefaultFormsUseCase()
    result = usecase.execute(include_questions=include_questions)

    if result.success:
        return success_response(result.data)
    else:
        return error_response(result.error, _get_status_code(result.error_code))


@forms_bp.route('/<int:form_id>/clone', methods=['POST'])
@jwt_required()
@admin_required
def clone_form(form_id):
    """Clone a default form for the company"""
    try:
        # Handle optional body - auto-generate name if not provided
        json_data = request.get_json(silent=True) or {}

        # If name provided, validate with schema; otherwise use default
        if json_data.get('name'):
            schema = CloneFormSchema()
            data = schema.load(json_data)
            new_name = data['name']
            description = data.get('description')
        else:
            # Auto-generate name based on original form
            from app.modules.forms.models import Form
            original_form = Form.query.get(form_id)
            if not original_form:
                return error_response('Form not found', 404)
            new_name = f"{original_form.name} (Copy)"
            description = json_data.get('description', original_form.description)

        user_id = get_jwt_identity()

        usecase = CloneFormUseCase()
        result = usecase.execute(
            form_id=form_id,
            user_id=user_id,
            new_name=new_name,
            description=description
        )

        if result.success:
            return success_response(
                result.data,
                message='Form cloned successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/company', methods=['GET'])
@jwt_required()
def list_company_forms():
    """List forms available to the current user's company"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    form_type = request.args.get('type')
    include_defaults = request.args.get('include_defaults', 'true').lower() == 'true'

    usecase = ListCompanyFormsUseCase()
    result = usecase.execute(
        user_id=user_id,
        include_defaults=include_defaults,
        form_type=form_type,
        page=page,
        per_page=per_page
    )

    if result.success:
        return success_response(result.data)
    else:
        return error_response(result.error, _get_status_code(result.error_code))


@forms_bp.route('/company', methods=['POST'])
@jwt_required()
@admin_required
def create_company_form():
    """Create a new form. Super Admin creates templates, Admin creates company-specific forms."""
    try:
        schema = CreateFormSchema()
        data = schema.load(request.json)
        user_id = get_jwt_identity()

        usecase = CreateCompanyFormUseCase()
        result = usecase.execute(
            name=data['name'],
            form_type=data['form_type'],
            user_id=user_id,
            description=data.get('description'),
            questions=data.get('questions')
        )

        if result.success:
            return success_response(
                result.data,
                message='Form created successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/<int:form_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_form_status(form_id):
    """Update form status (publish, archive, etc.)"""
    try:
        schema = UpdateFormStatusSchema()
        data = schema.load(request.json)
        user_id = get_jwt_identity()

        usecase = UpdateFormStatusUseCase()
        result = usecase.execute(form_id, user_id, data['status'])

        if result.success:
            return success_response(result.data, message='Form status updated successfully')
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


# ============== Question CRUD ==============

@forms_bp.route('/<int:form_id>/questions', methods=['POST'])
@jwt_required()
@admin_required
def add_question(form_id):
    """Add a question to a form (Admin can add to company forms)"""
    try:
        schema = AddQuestionSchema()
        data = schema.load(request.json)
        user_id = get_jwt_identity()

        # Verify access to form
        current_user = get_current_user()
        from app.modules.forms.models import Form
        form = Form.query.get(form_id)
        if not form:
            return error_response('Form not found', 404)

        # Check access: Super Admin can edit any, Admin can edit company forms only
        if current_user.role.name != 'super_admin':
            if form.company_id != current_user.company_id:
                return error_response('Access denied to this form', 403)

        usecase = AddQuestionUseCase()
        result = usecase.execute(form_id, data)

        if result.success:
            return success_response(
                result.data,
                message='Question added successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/questions/<int:question_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_question(question_id):
    """Update a question (Admin can update company form questions)"""
    try:
        schema = UpdateQuestionSchema()
        data = schema.load(request.json)

        # Verify access to question's form
        current_user = get_current_user()
        from app.modules.forms.models import FormQuestion
        question = FormQuestion.query.get(question_id)
        if not question:
            return error_response('Question not found', 404)

        # Check access
        if current_user.role.name != 'super_admin':
            if question.form.company_id != current_user.company_id:
                return error_response('Access denied to this question', 403)

        usecase = UpdateQuestionUseCase()
        result = usecase.execute(question_id, data)

        if result.success:
            return success_response(
                result.data,
                message='Question updated successfully'
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(question_id):
    """Delete a question (Admin can delete company form questions)"""
    # Verify access
    current_user = get_current_user()
    from app.modules.forms.models import FormQuestion
    question = FormQuestion.query.get(question_id)
    if not question:
        return error_response('Question not found', 404)

    # Check access
    if current_user.role.name != 'super_admin':
        if question.form.company_id != current_user.company_id:
            return error_response('Access denied to this question', 403)

    usecase = DeleteQuestionUseCase()
    result = usecase.execute(question_id)

    if result.success:
        return success_response(message='Question deleted successfully')
    else:
        return error_response(result.error, _get_status_code(result.error_code))


@forms_bp.route('/<int:form_id>/reorder', methods=['POST'])
@jwt_required()
@admin_required
def reorder_questions(form_id):
    """Reorder questions in a form (Admin can reorder company form questions)"""
    # Verify access
    current_user = get_current_user()
    from app.modules.forms.models import Form
    form = Form.query.get(form_id)
    if not form:
        return error_response('Form not found', 404)

    # Check access
    if current_user.role.name != 'super_admin':
        if form.company_id != current_user.company_id:
            return error_response('Access denied to this form', 403)

    question_orders = request.json.get('question_orders', [])

    usecase = ReorderQuestionsUseCase()
    result = usecase.execute(form_id, question_orders)

    if result.success:
        return success_response(
            result.data,
            message='Questions reordered successfully'
        )
    else:
        return error_response(result.error, _get_status_code(result.error_code))


# ============== Responses ==============

@forms_bp.route('/<int:form_id>/submit', methods=['POST'])
@jwt_required()
def submit_response(form_id):
    """Submit a response to a form"""
    try:
        schema = SubmitResponseSchema()
        data = schema.load(request.get_json(silent=True) or {})
        user_id = get_jwt_identity()

        # Staff can do partial saves (skip required field validation)
        partial = data.get('partial', False)
        if partial:
            current_user = get_current_user()
            if current_user.role.name not in ('super_admin', 'admin', 'senior_accountant', 'accountant'):
                partial = False  # Only staff can partial save

        usecase = SubmitFormResponseUseCase()
        result = usecase.execute(
            form_id=form_id,
            user_id=user_id,
            responses=data['responses'],
            service_request_id=data.get('service_request_id'),
            partial=partial
        )

        if result.success:
            return success_response(
                result.data,
                message='Response submitted successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/<int:form_id>/responses', methods=['POST'])
@jwt_required()
def submit_response_alias(form_id):
    """
    Submit a response to a form (alias route for POST /responses).
    This provides backward compatibility for clients using POST /responses instead of /submit.
    """
    try:
        schema = SubmitResponseSchema()
        data = schema.load(request.get_json(silent=True) or {})
        user_id = get_jwt_identity()

        # Staff can do partial saves (skip required field validation)
        partial = data.get('partial', False)
        if partial:
            current_user = get_current_user()
            if current_user.role.name not in ('super_admin', 'admin', 'senior_accountant', 'accountant'):
                partial = False

        usecase = SubmitFormResponseUseCase()
        result = usecase.execute(
            form_id=form_id,
            user_id=user_id,
            responses=data['responses'],
            service_request_id=data.get('service_request_id'),
            partial=partial
        )

        if result.success:
            return success_response(
                result.data,
                message='Response submitted successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@forms_bp.route('/<int:form_id>/responses', methods=['GET'])
@jwt_required()
@roles_required('super_admin', 'admin', 'senior_accountant', 'accountant')
def get_form_responses(form_id):
    """Get all responses for a form, optionally filtered by service request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    service_request_id = request.args.get('service_request_id')

    usecase = ListFormResponsesUseCase()
    result = usecase.execute(form_id, page, per_page, service_request_id=service_request_id)

    return success_response(result.data)


@forms_bp.route('/responses/<int:response_id>', methods=['GET'])
@jwt_required()
def get_response(response_id):
    """Get a specific response"""
    current_user = get_current_user()

    usecase = GetFormResponseUseCase()
    result = usecase.execute(response_id)

    if not result.success:
        return error_response(result.error, _get_status_code(result.error_code))

    # Users can only view their own responses unless admin/accountant
    response = result.data['response']
    if response.get('user_id') != current_user.id and \
       current_user.role.name not in ['super_admin', 'admin', 'senior_accountant', 'accountant']:
        return error_response('Access denied', 403)

    return success_response(result.data)


@forms_bp.route('/responses/<int:response_id>', methods=['PATCH'])
@jwt_required()
@roles_required('super_admin', 'admin', 'senior_accountant', 'accountant')
def update_response(response_id):
    """Update a form response (staff can edit client info)"""
    from app.modules.forms.models import FormResponse
    from app.modules.services.models import RequestAuditLog
    from app.extensions import db
    from datetime import datetime

    current_user = get_current_user()

    response = FormResponse.query.get(response_id)
    if not response:
        return error_response('Response not found', 404)

    # Check company access for admin
    if current_user.role.name == 'admin':
        if response.user and response.user.company_id != current_user.company_id:
            return error_response('Access denied', 403)

    data = request.json
    updated_responses = data.get('responses', [])

    if not updated_responses:
        return error_response('No responses provided', 400)

    # Track changes for audit log
    changes = {}
    old_response_data = response.response_data or {}
    old_responses = {str(r.get('question_id')): r.get('answer') for r in old_response_data.get('responses', [])}

    # Update the response_data
    new_response_items = []
    for item in updated_responses:
        question_id = str(item.get('question_id'))
        new_answer = item.get('answer')
        old_answer = old_responses.get(question_id)

        # Track change if value differs
        if str(old_answer) != str(new_answer):
            question_text = item.get('question_text', f'Question {question_id}')
            changes[f'form_response:{question_text}'] = (old_answer, new_answer)

        new_response_items.append({
            'question_id': item.get('question_id'),
            'question_text': item.get('question_text', ''),
            'question_type': item.get('question_type', 'text'),
            'section_number': item.get('section_number'),
            'section_title': item.get('section_title'),
            'answer': new_answer,
            'attachments': item.get('attachments', [])
        })

    # Update response_data
    response.response_data = {
        'form_snapshot': old_response_data.get('form_snapshot', {}),
        'responses': new_response_items,
        'metadata': {
            **old_response_data.get('metadata', {}),
            'last_modified_by': current_user.id,
            'last_modified_at': datetime.utcnow().isoformat()
        }
    }

    # Update legacy responses field
    response.responses = {str(item['question_id']): item['answer'] for item in new_response_items}

    # Merge repeatable instance answers (e.g. "123_2": "value")
    responses_dict = data.get('responses_dict', {})
    if responses_dict:
        for key, value in responses_dict.items():
            response.responses[str(key)] = value

    response.updated_at = datetime.utcnow()

    # Log changes to audit log if linked to a service request
    if response.service_request_id and changes:
        RequestAuditLog.log_changes(response.service_request_id, current_user.id, changes)

    db.session.commit()

    return success_response(
        {'response': response.to_dict(include_questions=True)},
        message='Response updated successfully'
    )
