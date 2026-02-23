"""
User Routes - User Management API Endpoints

User Management Endpoints (/api/users):
-------------------------------------
POST /api/users/invite
    Invite a new user (generates temp password).
    Required role: Admin or higher

POST /api/users/complete-onboarding
    Complete first-time onboarding (password change, profile).

PATCH /api/users/profile
    Update own user profile.

POST /api/users/change-password
    Change own password.

GET  /api/users
    List all users (admin sees company users only).
    Required role: Admin or higher

GET  /api/users/<user_id>
    Get user details.

PATCH /api/users/<user_id>
    Update a user's details.
    Required role: Staff

POST /api/users/<user_id>/toggle-status
    Activate/deactivate a user.
    Required role: Admin or higher

GET  /api/users/accountants
    Get list of accountants for assignment.
    Required role: Admin or higher

Client Notes Endpoints:
---------------------
GET  /api/users/<user_id>/notes
    Get notes for a client.

POST /api/users/<user_id>/notes
    Create a note on a client profile.

PATCH /api/users/notes/<note_id>
    Update a client note.

DELETE /api/users/notes/<note_id>
    Delete a client note.

PATCH /api/users/notes/<note_id>/pin
    Toggle pin status of a note.
"""
import logging
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError

from . import user_bp
from app.modules.user.models import User
from app.modules.user.usecases import (
    InviteUserUseCase,
    CompleteOnboardingUseCase,
    UpdateProfileUseCase,
    ChangePasswordUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    ToggleUserStatusUseCase,
    GetAccountantsUseCase,
    GetClientNotesUseCase,
    CreateClientNoteUseCase,
    UpdateClientNoteUseCase,
    DeleteClientNoteUseCase,
    ToggleNotePinUseCase,
    CheckDuplicatesUseCase
)
from app.modules.user.schemas import (
    InviteUserSchema, UpdatePasswordSchema,
    OnboardingSchema, StaffOnboardingSchema, UpdateProfileSchema
)
from app.common.decorators import roles_required, admin_required, accountant_required, get_current_user
from app.common.responses import success_response, error_response, paginated_response
from app.common.exceptions import APIException

# Module-level logger
logger = logging.getLogger(__name__)


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'INVALID_CREDENTIALS': 401,
        'INVALID_OTP': 401,
        'INVALID_EMAIL': 400,
        'INVALID_PASSWORD': 401,
        'ACCOUNT_INACTIVE': 403,
        'EMAIL_EXISTS': 409,
        'INVALID_ROLE': 400,
        'PASSWORD_MISMATCH': 400,
        'WEAK_PASSWORD': 400,
        'ALREADY_COMPLETED': 400,
        'FORBIDDEN': 403
    }
    return status_map.get(error_code, 400)


# ============== User Routes ==============

@user_bp.route('/invite', methods=['POST'])
@jwt_required()
@roles_required('super_admin', 'admin', 'senior_accountant')
def invite_user():
    """Invite a new user (Super Admin can invite to any company, Admin/Senior Accountant to their own)"""
    try:
        schema = InviteUserSchema()
        data = schema.load(request.json)
        current_user = get_current_user()

        # Define what roles each role can create
        # - Super admin: can invite all roles
        # - Admin: can invite senior_accountant, accountant, external_accountant, user
        # - Senior Accountant: can invite accountant, external_accountant, user
        # - Accountant: can invite external_accountant, user
        # - External accountant & user: cannot invite anyone
        role_permissions = {
            'super_admin': ['super_admin', 'admin', 'senior_accountant', 'accountant', 'external_accountant', 'user'],
            'admin': ['senior_accountant', 'accountant', 'external_accountant', 'user'],
            'senior_accountant': ['accountant', 'external_accountant', 'user'],
            'accountant': ['external_accountant', 'user']
        }

        allowed_roles = role_permissions.get(current_user.role.name, [])
        if data['role'] not in allowed_roles:
            return error_response(f'{current_user.role.name.replace("_", " ").title()} cannot create {data["role"]} users', 403)

        # Determine company_id
        if current_user.role.name == 'super_admin':
            # Super Admin can specify any company_id
            company_id = data.get('company_id')
            # If creating admin role, company_id is required
            if data['role'] in ['admin', 'senior_accountant'] and not company_id:
                return error_response('Company ID is required when creating an admin or senior accountant', 400)
        else:
            # Admin/Senior accountant uses their own company
            company_id = current_user.company_id

        # Handle supervisor_id for accountants
        supervisor_id = data.get('supervisor_id')
        # If a senior_accountant is inviting an accountant, automatically set themselves as supervisor
        if current_user.role.name == 'senior_accountant' and data['role'] == 'accountant':
            supervisor_id = current_user.id

        usecase = InviteUserUseCase()
        result = usecase.execute(
            email=data['email'],
            role_name=data['role'],
            invited_by_id=current_user.id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            company_id=company_id,
            supervisor_id=supervisor_id
        )

        if result.success:
            return success_response(
                {'user': result.data['user'], 'temp_password': result.data['temp_password']},
                message='User invited successfully',
                status_code=201
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@user_bp.route('/complete-onboarding', methods=['POST'])
@jwt_required()
def complete_onboarding():
    """Complete first-time onboarding"""
    try:
        user_id = get_jwt_identity()
        user = get_current_user()

        # Debug logging
        print(f"DEBUG: User ID: {user_id}")
        print(f"DEBUG: User: {user}")
        print(f"DEBUG: User role: {user.role.name if user else 'None'}")

        # Use simplified schema for staff users (admin/senior_accountant/accountant)
        if user and user.role.name in ['admin', 'senior_accountant', 'accountant']:
            print(f"DEBUG: Using StaffOnboardingSchema")
            schema = StaffOnboardingSchema()
        else:
            print(f"DEBUG: Using OnboardingSchema")
            schema = OnboardingSchema()

        data = schema.load(request.json)

        usecase = CompleteOnboardingUseCase()
        result = usecase.execute(user_id, data)

        if result.success:
            return success_response(
                {'user': result.data['user']},
                message='Onboarding completed successfully'
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@user_bp.route('/upload-document', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload ID document"""
    from app.modules.user.services import UserService

    try:
        user = get_current_user()

        if 'file' not in request.files:
            return error_response('No file provided', 400)

        file = request.files['file']
        if not file.filename:
            return error_response('No file selected', 400)

        result = UserService.upload_document(user, file)
        return success_response(result, message='Document uploaded successfully')
    except APIException as e:
        return error_response(e.message, e.status_code)


@user_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()

        schema = UpdateProfileSchema()
        data = schema.load(request.json)

        usecase = UpdateProfileUseCase()
        result = usecase.execute(user_id, data)

        if result.success:
            return success_response(
                {'user': result.data['user']},
                message='Profile updated successfully'
            )
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()

        schema = UpdatePasswordSchema()
        data = schema.load(request.json)

        usecase = ChangePasswordUseCase()
        result = usecase.execute(
            user_id,
            data.get('current_password', ''),
            data['new_password'],
            data['confirm_password']
        )

        if result.success:
            return success_response(result.data)
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@user_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """List all users (Admin only - filtered by company for practice admins)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role_filter = request.args.get('role')
    name_search = request.args.get('name')  # Search by name or email

    current_user = get_current_user()

    # Super admin sees all users, practice admin sees only their company users
    company_id = None
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    usecase = ListUsersUseCase()
    result = usecase.execute(role_filter, page, per_page, company_id, name_search)

    return paginated_response(
        result.data['users'],
        result.data['pagination']['page'],
        result.data['pagination']['per_page'],
        result.data['pagination']['total']
    )


@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    current_user = get_current_user()

    # Users can only view their own profile unless admin/accountant
    is_staff = current_user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
    if current_user.id != user_id and not is_staff:
        return error_response('Access denied', 403)

    # Users viewing their own profile or staff viewing clients get sensitive data
    include_sensitive = current_user.id == user_id
    if is_staff:
        target_user = User.query.get(user_id)
        if target_user:
            # Super admin can see all, others only their company users
            if current_user.role.name == 'super_admin':
                include_sensitive = True
            elif target_user.company_id == current_user.company_id:
                include_sensitive = True
            else:
                # Non-super-admin staff cannot access users from other companies
                return error_response('Access denied - user belongs to different company', 403)

    usecase = GetUserUseCase()
    result = usecase.execute(user_id, include_sensitive=include_sensitive)

    if result.success:
        return success_response({'user': result.data['user']})
    else:
        return error_response(result.error, _get_status_code(result.error_code))


@user_bp.route('/<user_id>', methods=['PATCH'])
@jwt_required()
@roles_required('super_admin', 'admin', 'senior_accountant', 'accountant')
def update_user(user_id):
    """Update a user's details (admin/accountant can update clients)"""
    from app.extensions import db

    current_user = get_current_user()
    target_user = User.query.get(user_id)

    if not target_user:
        return error_response('User not found', 404)

    # Check company access
    if current_user.role.name == 'admin':
        if target_user.company_id != current_user.company_id:
            return error_response('Cannot update users outside your company', 403)
    elif current_user.role.name == 'accountant':
        if target_user.company_id != current_user.company_id:
            return error_response('Cannot update users outside your company', 403)
        # Accountants can only update client users
        if target_user.role.name not in ['user']:
            return error_response('Accountants can only update client details', 403)

    data = request.json

    # Fields that can be updated
    allowed_fields = [
        'first_name', 'last_name', 'phone', 'address', 'date_of_birth',
        'occupation', 'company_name', 'personal_email',
        'tfn', 'visa_status',
        'bsb', 'bank_account_number', 'bank_account_holder_name',
        # Document URLs
        'passport_url', 'driving_licence_url', 'bank_statement_url', 'id_document_url'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(target_user, field, data[field])

    db.session.commit()

    return success_response(
        {'user': target_user.to_dict(include_sensitive=True)},
        message='User updated successfully'
    )


@user_bp.route('/<user_id>/toggle-status', methods=['POST'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    """Activate or deactivate a user"""
    is_active = request.json.get('is_active', True)

    usecase = ToggleUserStatusUseCase()
    result = usecase.execute(user_id, is_active)

    if result.success:
        return success_response(
            {'user': result.data['user']},
            message=result.data['message']
        )
    else:
        return error_response(result.error, _get_status_code(result.error_code))


@user_bp.route('/accountants', methods=['GET'])
@jwt_required()
@admin_required
def list_accountants():
    """Get list of accountants for assignment (filtered by company for practice admins)"""
    current_user = get_current_user()

    # Super admin sees all accountants, practice admin sees only their company's accountants
    company_id = None
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    usecase = GetAccountantsUseCase()
    result = usecase.execute(company_id=company_id)

    return success_response({'accountants': result.data['accountants']})


@user_bp.route('/senior-accountants', methods=['GET'])
@jwt_required()
@admin_required
def list_senior_accountants():
    """Get list of senior accountants for supervisor selection"""
    from app.modules.user.repositories import UserRepository

    current_user = get_current_user()
    user_repo = UserRepository()

    # Super admin sees all, others see only their company's
    company_id = None
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    senior_accountants = user_repo.get_senior_accountants(company_id=company_id)

    return success_response({
        'senior_accountants': [sa.to_dict() for sa in senior_accountants]
    })


@user_bp.route('/my-team', methods=['GET'])
@jwt_required()
@roles_required('senior_accountant')
def get_my_team():
    """Get accountants supervised by the current senior accountant"""
    from app.modules.user.repositories import UserRepository

    current_user = get_current_user()
    user_repo = UserRepository()

    supervised = user_repo.get_supervised_accountants(current_user.id)

    return success_response({
        'team': [a.to_dict() for a in supervised],
        'total': len(supervised)
    })


# ============== Client Notes Routes ==============

@user_bp.route('/<user_id>/notes', methods=['GET'])
@jwt_required()
@accountant_required
def get_client_notes(user_id):
    """Get notes for a client"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    usecase = GetClientNotesUseCase()
    result = usecase.execute(user_id, page, per_page)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@user_bp.route('/<user_id>/notes', methods=['POST'])
@jwt_required()
@accountant_required
def create_client_note(user_id):
    """Create a note on a client profile"""
    current_user = get_current_user()

    content = request.json.get('content')
    if not content:
        return error_response('Note content is required', 400)

    is_pinned = request.json.get('is_pinned', False)

    usecase = CreateClientNoteUseCase()
    result = usecase.execute(user_id, current_user.id, content, is_pinned)

    if result.success:
        return success_response(result.data, status_code=201)
    return error_response(result.error, _get_status_code(result.error_code))


@user_bp.route('/notes/<int:note_id>', methods=['PATCH'])
@jwt_required()
@accountant_required
def update_client_note(note_id):
    """Update a client note"""
    current_user = get_current_user()

    usecase = UpdateClientNoteUseCase()
    result = usecase.execute(note_id, request.json, current_user.id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@user_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
@accountant_required
def delete_client_note(note_id):
    """Delete a client note"""
    usecase = DeleteClientNoteUseCase()
    result = usecase.execute(note_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


@user_bp.route('/notes/<int:note_id>/pin', methods=['PATCH'])
@jwt_required()
@accountant_required
def toggle_note_pin(note_id):
    """Toggle pin status of a note"""
    usecase = ToggleNotePinUseCase()
    result = usecase.execute(note_id)

    if result.success:
        return success_response(result.data)
    return error_response(result.error, _get_status_code(result.error_code))


# ============== Duplicate Detection Routes ==============

@user_bp.route('/check-duplicates', methods=['POST'])
@jwt_required()
@accountant_required
def check_duplicates():
    """Check for potential duplicate users"""
    current_user = get_current_user()

    company_id = current_user.company_id
    if current_user.role.name == 'super_admin':
        company_id = request.json.get('company_id')

    usecase = CheckDuplicatesUseCase()
    result = usecase.execute(request.json, company_id)

    return success_response(result.data)


# ============== Export Routes ==============

@user_bp.route('/export', methods=['GET'])
@jwt_required()
@admin_required
def export_users():
    """Export users to CSV or Excel"""
    from app.common.export import generate_csv, generate_excel, USER_EXPORT_COLUMNS

    format_type = request.args.get('format', 'csv')
    role_filter = request.args.get('role')

    current_user = get_current_user()

    # Get users
    query = User.query
    if current_user.role.name != 'super_admin':
        query = query.filter(User.company_id == current_user.company_id)

    if role_filter:
        from app.modules.user.models import Role
        role = Role.query.filter_by(name=role_filter).first()
        if role:
            query = query.filter(User.role_id == role.id)

    users = query.order_by(User.created_at.desc()).all()
    data = [u.to_dict() for u in users]

    filename = f'users_export_{request.args.get("role", "all")}'

    if format_type == 'excel':
        return generate_excel(data, USER_EXPORT_COLUMNS, filename)
    return generate_csv(data, USER_EXPORT_COLUMNS, filename)


# ============== Import Routes ==============

@user_bp.route('/import/template', methods=['GET'])
@jwt_required()
@admin_required
def download_import_template():
    """Download CSV template for client import"""
    import csv
    import io
    from flask import Response

    # Define template columns with sample data
    template_columns = [
        'email',
        'first_name',
        'last_name',
        'phone',
        'address',
        'date_of_birth',
        'occupation',
        'company_name',
        'abn',
        'tfn',
        'personal_email',
        'bsb',
        'bank_account_number',
        'bank_account_holder_name'
    ]

    # Sample data rows
    sample_rows = [
        {
            'email': 'john.smith@example.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'phone': '0412345678',
            'address': '123 Main Street, Sydney NSW 2000',
            'date_of_birth': '1985-06-15',
            'occupation': 'Software Engineer',
            'company_name': 'Smith Tech Pty Ltd',
            'abn': '12345678901',
            'tfn': '',
            'personal_email': 'john.personal@gmail.com',
            'bsb': '062-000',
            'bank_account_number': '12345678',
            'bank_account_holder_name': 'John Smith'
        },
        {
            'email': 'jane.doe@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '0498765432',
            'address': '456 Oak Avenue, Melbourne VIC 3000',
            'date_of_birth': '1990-03-22',
            'occupation': 'Marketing Manager',
            'company_name': '',
            'abn': '',
            'tfn': '',
            'personal_email': '',
            'bsb': '',
            'bank_account_number': '',
            'bank_account_holder_name': ''
        }
    ]

    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=template_columns)
    writer.writeheader()
    for row in sample_rows:
        writer.writerow(row)

    # Return as downloadable file
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=client_import_template.csv',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )
    return response


@user_bp.route('/import', methods=['POST'])
@jwt_required()
@admin_required
def import_clients():
    """Import clients from CSV file"""
    import csv
    import io
    from app.extensions import db
    from app.modules.user.models import User, Role
    from werkzeug.security import generate_password_hash
    import secrets
    import string

    current_user = get_current_user()

    if 'file' not in request.files:
        return error_response('No file provided', 400)

    file = request.files['file']
    if not file or not file.filename:
        return error_response('No file selected', 400)

    # Validate file type
    if not file.filename.endswith('.csv'):
        return error_response('Only CSV files are supported', 400)

    # Read CSV content
    try:
        content = file.read().decode('utf-8-sig')  # Handle BOM
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
    except Exception as e:
        return error_response(f'Failed to parse CSV: {str(e)}', 400)

    if not rows:
        return error_response('CSV file is empty', 400)

    # Validate required columns
    required_columns = ['email', 'first_name', 'last_name']
    missing_columns = [col for col in required_columns if col not in reader.fieldnames]
    if missing_columns:
        return error_response(f'Missing required columns: {", ".join(missing_columns)}', 400)

    # Get client role
    client_role = Role.query.filter_by(name='user').first()
    if not client_role:
        return error_response('Client role not found in system', 500)

    # Determine company_id
    if current_user.role.name == 'super_admin':
        company_id = request.form.get('company_id') or current_user.company_id
    else:
        company_id = current_user.company_id

    # Process rows
    results = {
        'total': len(rows),
        'imported': 0,
        'skipped': 0,
        'errors': []
    }

    imported_users = []

    for idx, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
        email = row.get('email', '').strip().lower()

        # Skip empty rows
        if not email:
            results['skipped'] += 1
            continue

        # Validate email format
        if '@' not in email or '.' not in email:
            results['errors'].append({
                'row': idx,
                'email': email,
                'error': 'Invalid email format'
            })
            results['skipped'] += 1
            continue

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            results['errors'].append({
                'row': idx,
                'email': email,
                'error': 'Email already exists'
            })
            results['skipped'] += 1
            continue

        # Generate temporary password
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        try:
            # Create user
            new_user = User(
                email=email,
                password_hash=generate_password_hash(temp_password),
                first_name=row.get('first_name', '').strip() or None,
                last_name=row.get('last_name', '').strip() or None,
                phone=row.get('phone', '').strip() or None,
                address=row.get('address', '').strip() or None,
                date_of_birth=row.get('date_of_birth', '').strip() or None,
                occupation=row.get('occupation', '').strip() or None,
                company_name=row.get('company_name', '').strip() or None,
                tfn=row.get('tfn', '').strip() or None,
                personal_email=row.get('personal_email', '').strip() or None,
                bsb=row.get('bsb', '').strip() or None,
                bank_account_number=row.get('bank_account_number', '').strip() or None,
                bank_account_holder_name=row.get('bank_account_holder_name', '').strip() or None,
                role_id=client_role.id,
                company_id=company_id,
                is_active=True,
                is_first_login=True
            )

            db.session.add(new_user)
            db.session.flush()  # Get ID without committing

            imported_users.append({
                'email': email,
                'name': f"{row.get('first_name', '')} {row.get('last_name', '')}".strip(),
                'temp_password': temp_password
            })

            results['imported'] += 1

        except Exception as e:
            results['errors'].append({
                'row': idx,
                'email': email,
                'error': str(e)
            })
            results['skipped'] += 1

    # Commit all successful imports
    if results['imported'] > 0:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return error_response(f'Failed to save imports: {str(e)}', 500)

    return success_response({
        'results': results,
        'imported_users': imported_users[:10],  # Only return first 10 for display
        'message': f"Successfully imported {results['imported']} of {results['total']} clients"
    })
