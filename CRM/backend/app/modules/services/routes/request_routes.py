"""
Service Request Routes - Thin Controllers

These routes handle HTTP concerns and delegate business logic to use cases.
"""
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError

from . import requests_bp
from app.modules.services.usecases import (
    CreateServiceRequestUseCase,
    CreateMultipleRequestsUseCase,
    GetServiceRequestUseCase,
    ListServiceRequestsUseCase,
    AssignRequestUseCase,
    UpdateRequestStatusUseCase,
    UpdateInvoiceUseCase,
    AddInternalNoteUseCase,
    UpdateRequestUseCase,
    ReassignRequestUseCase,
    UpdateCostUseCase,
    GetDashboardMetricsUseCase,
)
from app.modules.services.schemas import (
    CreateRequestSchema,
    CreateMultipleRequestsSchema,
    AssignRequestSchema,
    UpdateStatusSchema,
    UpdateInvoiceSchema,
    UpdateCostSchema,
    AddNoteSchema,
)
from app.common.decorators import admin_required, accountant_required, invoice_admin_required, get_current_user
from app.common.responses import success_response, error_response


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'FORBIDDEN': 403,
        'INVALID_ROLE': 400,
        'INVALID_STATUS': 400,
        'SERVICE_INACTIVE': 400,
        'INVOICE_NOT_RAISED': 400,
    }
    return status_map.get(error_code, 400)


# ============== Service Request Routes ==============

@requests_bp.route('/', methods=['GET'])
@jwt_required()
def list_requests():
    """List service requests (filtered by role)"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    company_id = request.args.get('company_id')
    service_id = request.args.get('service_id', type=int)
    invoice_status = request.args.get('invoice_status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search')
    accountant_id = request.args.get('accountant_id')
    client_user_id = request.args.get('user_id')

    usecase = ListServiceRequestsUseCase()
    result = usecase.execute(
        user_id, status, page, per_page,
        company_id=company_id, service_id=service_id,
        invoice_status=invoice_status, date_from=date_from,
        date_to=date_to, search=search, accountant_id=accountant_id,
        client_user_id=client_user_id
    )

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@requests_bp.route('/', methods=['POST'])
@jwt_required()
def create_request():
    """Create a service request (admins can create on behalf of users)"""
    try:
        current_user = get_current_user()
        requester_id = get_jwt_identity()

        # Check if admin is creating on behalf of a user
        target_user_id = request.json.get('user_id')
        if target_user_id:
            if current_user.role.name not in ['super_admin', 'admin']:
                return error_response('Only admins can create requests on behalf of users', 403)

            from app.modules.user.models import User
            target_user = User.query.get(target_user_id)
            if not target_user:
                return error_response('Target user not found', 404)

            if current_user.role.name == 'admin' and target_user.company_id != current_user.company_id:
                return error_response('Cannot create requests for users outside your company', 403)

            user_id = target_user_id
        else:
            user_id = requester_id

        # Check if multiple services
        if 'service_ids' in request.json:
            schema = CreateMultipleRequestsSchema()
            data = schema.load(request.json)

            usecase = CreateMultipleRequestsUseCase()
            result = usecase.execute(
                user_id, data['service_ids'],
                description=data.get('description'),
                internal_reference=data.get('internal_reference'),
                xero_reference_job_id=data.get('xero_reference_job_id'),
                client_entity_id=data.get('client_entity_id')
            )

            if result.success:
                return success_response(
                    result.data,
                    message=f'{result.data["count"]} request(s) created successfully',
                    status_code=201
                )
            return error_response(result.error, _get_status_code(result.error_code))
        else:
            schema = CreateRequestSchema()
            data = schema.load(request.json)

            usecase = CreateServiceRequestUseCase()
            result = usecase.execute(
                user_id, data['service_id'],
                description=data.get('description'),
                internal_reference=data.get('internal_reference'),
                xero_reference_job_id=data.get('xero_reference_job_id'),
                client_entity_id=data.get('client_entity_id')
            )

            if result.success:
                return success_response(result.data, message='Request created successfully', status_code=201)
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@requests_bp.route('/draft', methods=['POST'])
@jwt_required()
def save_draft():
    """Save or update a draft service request with form responses"""
    from app.extensions import db
    from app.modules.services.models import ServiceRequest
    from app.modules.forms.models import FormResponse, Form
    from app.modules.user.models import User

    current_user = get_current_user()
    data = request.json or {}

    service_ids = data.get('service_ids', [])
    form_responses = data.get('form_responses', {})  # {service_id: {form_id, responses}}
    client_entity_id = data.get('client_entity_id')
    draft_id = data.get('draft_id')  # If updating an existing draft
    target_user_id = data.get('user_id')

    if not service_ids:
        return error_response('At least one service is required', 400)

    # Determine the user (admin can create on behalf)
    user_id = current_user.id
    if target_user_id and current_user.role.name in ['super_admin', 'admin']:
        user_id = target_user_id

    try:
        created_requests = []

        if draft_id:
            # Update existing draft - find all draft requests for this draft group
            existing_drafts = ServiceRequest.query.filter_by(
                id=draft_id, user_id=user_id, status=ServiceRequest.STATUS_DRAFT
            ).all()

            if not existing_drafts:
                return error_response('Draft not found', 404)

        # Create/update draft requests for each service
        for service_id in service_ids:
            # Check if there's already a draft for this user + service
            existing = None
            if draft_id:
                existing = ServiceRequest.query.filter_by(
                    id=draft_id, status=ServiceRequest.STATUS_DRAFT
                ).first()

            if existing:
                sr = existing
            else:
                # Check for existing draft for same user + service
                existing = ServiceRequest.query.filter_by(
                    user_id=user_id, service_id=service_id,
                    status=ServiceRequest.STATUS_DRAFT
                ).first()

                if existing:
                    sr = existing
                else:
                    sr = ServiceRequest(
                        user_id=user_id,
                        service_id=service_id,
                        request_number=ServiceRequest.generate_request_number(),
                        status=ServiceRequest.STATUS_DRAFT,
                        client_entity_id=client_entity_id,
                    )
                    db.session.add(sr)
                    db.session.flush()  # Get the ID

            # Save form responses for this service
            svc_key = str(service_id)
            if svc_key in form_responses:
                fr_data = form_responses[svc_key]
                form_id = fr_data.get('form_id')
                responses = fr_data.get('responses', {})

                if form_id and responses:
                    # Check if draft form response already exists
                    existing_fr = FormResponse.query.filter_by(
                        service_request_id=sr.id,
                        form_id=form_id,
                        status=FormResponse.STATUS_DRAFT
                    ).first()

                    form = Form.query.get(form_id)
                    if form:
                        if existing_fr:
                            # Update existing draft response
                            existing_fr.response_data = {
                                'form_snapshot': {
                                    'id': form.id,
                                    'name': form.name,
                                    'description': form.description,
                                    'form_type': form.form_type,
                                },
                                'responses': [
                                    {'question_id': k, 'answer': v}
                                    for k, v in responses.items()
                                ],
                                'metadata': {'status': 'draft'}
                            }
                            existing_fr.responses = responses
                        else:
                            fr = FormResponse(
                                form_id=form_id,
                                user_id=user_id,
                                service_request_id=sr.id,
                                status=FormResponse.STATUS_DRAFT,
                                response_data={
                                    'form_snapshot': {
                                        'id': form.id,
                                        'name': form.name,
                                        'description': form.description,
                                        'form_type': form.form_type,
                                    },
                                    'responses': [
                                        {'question_id': k, 'answer': v}
                                        for k, v in responses.items()
                                    ],
                                    'metadata': {'status': 'draft'}
                                },
                                responses=responses,
                            )
                            db.session.add(fr)

            created_requests.append(sr)

        db.session.commit()

        return success_response({
            'drafts': [r.to_dict() for r in created_requests],
            'count': len(created_requests),
        }, message='Draft saved successfully', status_code=201)

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to save draft: {str(e)}', 500)


@requests_bp.route('/drafts', methods=['GET'])
@jwt_required()
def list_drafts():
    """List current user's draft service requests"""
    from app.modules.services.models import ServiceRequest
    from app.modules.forms.models import FormResponse

    current_user = get_current_user()
    drafts = ServiceRequest.query.filter_by(
        user_id=current_user.id,
        status=ServiceRequest.STATUS_DRAFT
    ).order_by(ServiceRequest.updated_at.desc()).all()

    result = []
    for draft in drafts:
        d = draft.to_dict()
        # Include form response data so frontend can restore form state
        fr = FormResponse.query.filter_by(
            service_request_id=draft.id,
            status=FormResponse.STATUS_DRAFT
        ).first()
        if fr:
            d['form_response'] = {
                'form_id': fr.form_id,
                'responses': fr.responses or {},
            }
        result.append(d)

    return success_response({'drafts': result, 'count': len(result)})


@requests_bp.route('/<request_id>/submit-draft', methods=['POST'])
@jwt_required()
def submit_draft(request_id):
    """Convert a draft request to pending status (final submit)"""
    from app.extensions import db
    from app.modules.services.models import ServiceRequest
    from app.modules.forms.models import FormResponse
    from app.modules.user.models import User, Role
    from app.modules.notifications.services import NotificationService

    current_user = get_current_user()

    sr = ServiceRequest.query.get(request_id)
    if not sr:
        return error_response('Request not found', 404)
    if sr.user_id != current_user.id:
        return error_response('Access denied', 403)
    if sr.status != ServiceRequest.STATUS_DRAFT:
        return error_response('Request is not a draft', 400)

    # Update status to pending
    sr.status = ServiceRequest.STATUS_PENDING

    # Update any draft form responses to submitted
    draft_responses = FormResponse.query.filter_by(
        service_request_id=sr.id,
        status=FormResponse.STATUS_DRAFT
    ).all()
    for fr in draft_responses:
        fr.status = FormResponse.STATUS_SUBMITTED

    db.session.commit()

    # Notify admins
    try:
        request_user = User.query.get(sr.user_id)
        if request_user and request_user.company_id:
            admin_role = Role.query.filter_by(name=Role.ADMIN).first()
            admins = User.query.filter(
                User.role_id == admin_role.id,
                User.company_id == request_user.company_id,
                User.is_active == True
            ).all()
            if admins:
                NotificationService.send_new_request_notification(sr, admins)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Failed to notify admins: {str(e)}')

    return success_response({'request': sr.to_dict()}, message='Request submitted successfully')


@requests_bp.route('/<request_id>', methods=['GET'])
@jwt_required()
def get_request(request_id):
    """Get a service request by ID"""
    current_user = get_current_user()

    usecase = GetServiceRequestUseCase()
    result = usecase.execute(request_id)

    if not result.success:
        return error_response(result.error, _get_status_code(result.error_code))

    # Check access
    service_request = result.data['request']
    is_staff = current_user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
    is_owner = service_request.get('user', {}).get('id') == current_user.id

    if not is_staff and not is_owner:
        return error_response('Access denied', 403)

    # Re-fetch with notes if staff
    if is_staff:
        result = usecase.execute(request_id, include_notes=True)

    return success_response(result.data)


@requests_bp.route('/<request_id>', methods=['PATCH'])
@jwt_required()
def update_request(request_id):
    """Update a service request (admin/owner can edit, changes are audited)"""
    current_user = get_current_user()
    data = request.json

    is_admin = current_user.role.name in ['super_admin', 'admin']

    usecase = UpdateRequestUseCase()
    result = usecase.execute(request_id, current_user.id, data, is_admin=is_admin)

    if result.success:
        return success_response(result.data, message='Request updated successfully')
    return error_response(result.error, _get_status_code(result.error_code))


@requests_bp.route('/<request_id>/assign', methods=['POST', 'PUT'])
@jwt_required()
@accountant_required
def assign_request(request_id):
    """Assign a request to an accountant with optional deadline and priority (admin or accountant)"""
    try:
        schema = AssignRequestSchema()
        data = schema.load(request.get_json(silent=True) or {})
        user_id = get_jwt_identity()

        usecase = AssignRequestUseCase()
        result = usecase.execute(
            request_id, data['accountant_id'], user_id,
            deadline_date=data.get('deadline_date'),
            priority=data.get('priority')
        )

        if result.success:
            return success_response(result.data, message='Request assigned successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@requests_bp.route('/<request_id>/reassign', methods=['POST'])
@jwt_required()
@accountant_required
def reassign_request(request_id):
    """Reassign a request to another accountant"""
    current_user = get_current_user()
    data = request.get_json(silent=True) or {}
    new_accountant_id = data.get('accountant_id')
    reason = data.get('reason', '')

    if not new_accountant_id:
        return error_response('New accountant ID is required', 400)

    usecase = ReassignRequestUseCase()
    result = usecase.execute(request_id, new_accountant_id, current_user.id, reason=reason)

    if result.success:
        return success_response(result.data, message=result.data.get('message', 'Request reassigned'))
    return error_response(result.error, _get_status_code(result.error_code))


@requests_bp.route('/<request_id>/status', methods=['PATCH'])
@jwt_required()
@accountant_required
def update_request_status(request_id):
    """Update request status"""
    try:
        schema = UpdateStatusSchema()
        data = schema.load(request.json)
        user_id = get_jwt_identity()
        current_user = get_current_user()
        user_role = current_user.role.name if current_user and current_user.role else None

        usecase = UpdateRequestStatusUseCase()
        result = usecase.execute(request_id, data['status'], user_id, user_role=user_role)

        if result.success:
            return success_response(result.data, message='Status updated successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@requests_bp.route('/<request_id>/invoice', methods=['PATCH'])
@jwt_required()
@invoice_admin_required
def update_invoice(request_id):
    """Update invoice details (admin/accountant only - senior_accountant excluded)"""
    try:
        schema = UpdateInvoiceSchema()
        data = schema.load(request.get_json(silent=True) or {})
        user_id = get_jwt_identity()

        usecase = UpdateInvoiceUseCase()
        result = usecase.execute(
            request_id, updated_by_id=user_id,
            invoice_raised=data.get('invoice_raised'),
            invoice_paid=data.get('invoice_paid'),
            invoice_amount=data.get('invoice_amount'),
            payment_link=data.get('payment_link')
        )

        if result.success:
            return success_response(result.data, message='Invoice updated successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@requests_bp.route('/<request_id>/cost', methods=['PATCH'])
@jwt_required()
@accountant_required
def update_cost(request_id):
    """Update cost details for a service request (Admin/Accountant only)"""
    try:
        schema = UpdateCostSchema()
        data = schema.load(request.get_json(silent=True) or {})
        current_user = get_current_user()

        usecase = UpdateCostUseCase()
        result = usecase.execute(
            request_id, current_user.id,
            actual_cost=data.get('actual_cost'),
            cost_notes=data.get('cost_notes'),
            labor_hours=data.get('labor_hours'),
            labor_rate=data.get('labor_rate')
        )

        if result.success:
            return success_response(result.data, message='Cost details updated successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@requests_bp.route('/<request_id>/notes', methods=['POST'])
@jwt_required()
@accountant_required
def add_internal_note(request_id):
    """Add internal note to a request"""
    try:
        schema = AddNoteSchema()
        data = schema.load(request.json)
        user_id = get_jwt_identity()

        usecase = AddInternalNoteUseCase()
        result = usecase.execute(request_id, data['note'], user_id)

        if result.success:
            return success_response(result.data, message='Note added successfully')
        return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


# ============== Dashboard Routes ==============

@requests_bp.route('/dashboard/metrics', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    """Get dashboard metrics filtered by role"""
    user_id = get_jwt_identity()
    company_id = request.args.get('company_id')

    usecase = GetDashboardMetricsUseCase()
    result = usecase.execute(user_id, company_id=company_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


# ============== Audit Log Routes ==============

@requests_bp.route('/<request_id>/audit-log', methods=['GET'])
@jwt_required()
def get_request_audit_log(request_id):
    """Get audit log for a service request"""
    from app.modules.services.models import ServiceRequest, RequestAuditLog

    current_user = get_current_user()
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return error_response('Request not found', 404)

    is_staff = current_user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
    is_owner = service_request.user_id == current_user.id

    if not is_staff and not is_owner:
        return error_response('Access denied', 403)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    pagination = RequestAuditLog.query.filter_by(service_request_id=request_id)\
        .order_by(RequestAuditLog.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return success_response({
        'audit_logs': [log.to_dict() for log in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


# ============== Assignment History Routes ==============

@requests_bp.route('/<request_id>/assignment-history', methods=['GET'])
@jwt_required()
@accountant_required
def get_assignment_history(request_id):
    """Get assignment history for a request"""
    from app.modules.services.models import ServiceRequest, AssignmentHistory

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return error_response('Request not found', 404)

    history = AssignmentHistory.query.filter_by(service_request_id=request_id)\
        .order_by(AssignmentHistory.created_at.desc()).all()

    return success_response({
        'history': [h.to_dict() for h in history],
        'total': len(history)
    })


# ============== State History Routes ==============

@requests_bp.route('/<request_id>/state-history', methods=['GET'])
@jwt_required()
@accountant_required
def get_state_history(request_id):
    """Get state change history for a request"""
    from app.modules.services.models import ServiceRequest, RequestStateHistory

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return error_response('Request not found', 404)

    history = RequestStateHistory.query.filter_by(service_request_id=request_id)\
        .order_by(RequestStateHistory.changed_at.asc()).all()

    # Get duration summary
    durations = RequestStateHistory.get_state_durations(request_id)
    duration_summary = []
    for state, seconds in durations.items():
        duration_summary.append({
            'state': state,
            'duration_seconds': int(seconds),
            'duration_formatted': RequestStateHistory._format_duration(int(seconds))
        })

    return success_response({
        'history': [h.to_dict() for h in history],
        'duration_summary': duration_summary,
        'total_history_entries': len(history)
    })


# ============== Job Notes Routes ==============

@requests_bp.route('/<request_id>/job-notes', methods=['GET'])
@jwt_required()
@accountant_required
def get_job_notes(request_id):
    """Get all job notes for a request"""
    from app.modules.services.models import ServiceRequest, JobNote

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return error_response('Request not found', 404)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    note_type = request.args.get('type')

    query = JobNote.query.filter_by(service_request_id=request_id)
    if note_type:
        query = query.filter_by(note_type=note_type)

    pagination = query.order_by(JobNote.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return success_response({
        'job_notes': [n.to_dict() for n in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@requests_bp.route('/<request_id>/job-notes', methods=['POST'])
@jwt_required()
@accountant_required
def create_job_note(request_id):
    """Create a job note on a request"""
    from app.modules.services.models import ServiceRequest, JobNote
    from app.extensions import db

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return error_response('Request not found', 404)

    content = request.json.get('content')
    if not content:
        return error_response('Note content is required', 400)

    note_type = request.json.get('note_type', 'general')
    if note_type not in JobNote.VALID_TYPES:
        return error_response(f'Invalid note type. Valid types: {JobNote.VALID_TYPES}', 400)

    time_spent = request.json.get('time_spent_minutes', 0)
    current_user = get_current_user()

    job_note = JobNote(
        service_request_id=request_id,
        created_by_id=current_user.id,
        note_type=note_type,
        content=content,
        time_spent_minutes=time_spent
    )

    db.session.add(job_note)
    db.session.commit()

    return success_response({'job_note': job_note.to_dict()}, status_code=201)


# ============== Form Responses Routes ==============

@requests_bp.route('/<request_id>/form-responses', methods=['GET'])
@jwt_required()
def get_request_form_responses(request_id):
    """Get form responses for a service request"""
    from app.modules.services.models import ServiceRequest
    from app.modules.forms.models import FormResponse

    current_user = get_current_user()
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return error_response('Request not found', 404)

    is_staff = current_user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
    is_owner = service_request.user_id == current_user.id

    if not is_staff and not is_owner:
        return error_response('Access denied', 403)

    responses = FormResponse.query.filter_by(service_request_id=request_id).all()

    return success_response({
        'form_responses': [r.to_dict(include_questions=True) for r in responses],
        'total': len(responses)
    })
