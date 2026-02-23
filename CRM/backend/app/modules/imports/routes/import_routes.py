"""
Data Import Routes - Bulk CSV Import API Endpoints

This module provides REST API endpoints for importing data from CSV files.
Supports importing clients, service requests, services catalog, and companies.

Endpoints:
---------
GET  /api/imports/templates/<data_type>
    Download CSV template for a specific data type.
    Valid types: 'clients', 'service_requests', 'services', 'companies'
    Required role: Admin or higher

POST /api/imports/clients
    Import clients/users from CSV file.
    Required columns: email, first_name, last_name
    Optional: phone, address, date_of_birth, occupation, company_name, abn, tfn
    Required role: Admin or higher

POST /api/imports/service-requests
    Import service requests from CSV file.
    Required columns: client_email, service_name
    Optional: status, description, priority, deadline_date, invoice_amount
    Required role: Admin or higher

POST /api/imports/services
    Import/update services catalog from CSV file.
    Required columns: name
    Optional: description, category, base_price, is_recurring, renewal_period_months
    Required role: Admin or higher

POST /api/imports/companies
    Import companies with admin users from CSV file.
    Required columns: name, admin_email
    Optional: trading_name, abn, acn, email, phone, address, website
    Required role: Super Admin only

GET  /api/imports/available-types
    Get list of available import types for current user.
    Required role: Admin or higher
"""
import logging
from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.modules.user.models import User
from app.common.responses import success_response, error_response
from app.common.decorators import admin_required, super_admin_required
from app.modules.imports.usecases import (
    GetTemplateUseCase,
    ImportClientsUseCase,
    ImportServiceRequestsUseCase,
    ImportServicesUseCase,
    ImportCompaniesUseCase,
    GetAvailableTypesUseCase
)

logger = logging.getLogger(__name__)

import_bp = Blueprint('imports', __name__, url_prefix='/api/imports')


def get_current_user() -> User:
    """Get current user from JWT."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


# ============== Template Downloads ==============

@import_bp.route('/templates/<data_type>', methods=['GET'])
@jwt_required()
@admin_required
def download_template(data_type: str):
    """
    Download CSV template for a specific data type.

    Provides a pre-formatted CSV file with correct column headers
    and sample data rows to guide users in preparing import files.

    Args:
        data_type: One of 'clients', 'service_requests', 'services', 'companies'

    Returns:
        CSV file download with appropriate headers and sample data
    """
    logger.info(f"GET /imports/templates/{data_type} - Template download requested")

    csv_content, filename, error = GetTemplateUseCase.execute(data_type)

    if error:
        logger.warning(f"Invalid template type requested: {data_type}")
        return error_response(error, 400)

    response = Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )
    return response


# ============== Import Endpoints ==============

@import_bp.route('/clients', methods=['POST'])
@jwt_required()
@admin_required
def import_clients():
    """
    Import clients/users from CSV file.

    Creates new user accounts for each valid row in the CSV.
    Generates temporary passwords for each user that should be
    changed on first login.

    Returns:
        Import results with counts of imported, skipped, and errors
        Plus list of imported users with temporary passwords
    """
    current_user = get_current_user()
    logger.info(f"POST /imports/clients - Client import by user_id={current_user.id}")

    # Validate file
    file_error = _validate_csv_file()
    if file_error:
        return file_error

    # Read CSV content
    csv_content, parse_error = _read_csv_content()
    if parse_error:
        return parse_error

    # Determine company_id
    company_id = _get_company_id(current_user)

    # Execute use case
    use_case = ImportClientsUseCase()
    result, imported_users, error = use_case.execute(csv_content, company_id)

    if error:
        return error_response(error, 400)

    return success_response({
        'message': f"Successfully imported {result.imported} clients",
        'results': result.to_dict(),
        'imported_users': [u.to_dict() for u in imported_users[:20]]
    })


@import_bp.route('/service-requests', methods=['POST'])
@jwt_required()
@admin_required
def import_service_requests():
    """
    Import service requests from CSV file.

    Creates new service requests linking clients to services.
    Clients must already exist in the system (matched by email).
    Services are matched by name (case-insensitive).

    Returns:
        Import results with counts and list of created requests
    """
    current_user = get_current_user()
    logger.info(f"POST /imports/service-requests - Request import by user_id={current_user.id}")

    # Validate file
    file_error = _validate_csv_file()
    if file_error:
        return file_error

    # Read CSV content
    csv_content, parse_error = _read_csv_content()
    if parse_error:
        return parse_error

    # Determine company_id
    company_id = _get_company_id(current_user)

    # Execute use case
    use_case = ImportServiceRequestsUseCase()
    result, imported_requests, error = use_case.execute(csv_content, company_id)

    if error:
        return error_response(error, 400)

    return success_response({
        'message': f"Successfully imported {result.imported} service requests",
        'results': result.to_dict(),
        'imported_requests': [r.to_dict() for r in imported_requests[:20]]
    })


@import_bp.route('/services', methods=['POST'])
@jwt_required()
@admin_required
def import_services():
    """
    Import or update services catalog from CSV file.

    Creates new services or updates existing ones (matched by name).
    This allows bulk management of the service offerings.

    Returns:
        Import results with counts of new imports and updates
    """
    current_user = get_current_user()
    logger.info(f"POST /imports/services - Service catalog import by user_id={current_user.id}")

    # Validate file
    file_error = _validate_csv_file()
    if file_error:
        return file_error

    # Read CSV content
    csv_content, parse_error = _read_csv_content()
    if parse_error:
        return parse_error

    # Execute use case
    use_case = ImportServicesUseCase()
    result, error = use_case.execute(csv_content)

    if error:
        return error_response(error, 400)

    return success_response({
        'message': f"Imported {result.imported} new services, updated {result.updated} existing",
        'results': result.to_dict()
    })


@import_bp.route('/companies', methods=['POST'])
@jwt_required()
@super_admin_required
def import_companies():
    """
    Import companies with admin users from CSV file.

    Creates new companies and their initial admin user accounts.
    This is a super_admin only operation for onboarding new practices.

    Returns:
        Import results with company names and admin credentials
    """
    current_user = get_current_user()
    logger.info(f"POST /imports/companies - Company import by super_admin user_id={current_user.id}")

    # Validate file
    file_error = _validate_csv_file()
    if file_error:
        return file_error

    # Read CSV content
    csv_content, parse_error = _read_csv_content()
    if parse_error:
        return parse_error

    # Execute use case
    use_case = ImportCompaniesUseCase()
    result, imported_companies, error = use_case.execute(csv_content)

    if error:
        return error_response(error, 400)

    return success_response({
        'message': f"Successfully imported {result.imported} companies",
        'results': result.to_dict(),
        'imported_companies': [c.to_dict() for c in imported_companies]
    })


@import_bp.route('/available-types', methods=['GET'])
@jwt_required()
@admin_required
def get_available_import_types():
    """
    Get list of available import types for current user.

    Returns metadata about each import type including required
    and optional columns. Super admins see the companies import option.

    Returns:
        Array of import type definitions with column specifications
    """
    current_user = get_current_user()
    logger.debug(f"GET /imports/available-types by user_id={current_user.id}")

    is_super_admin = current_user.role.name == 'super_admin'
    import_types = GetAvailableTypesUseCase.execute(is_super_admin)

    return success_response({
        'types': [t.to_dict() for t in import_types]
    })


# ============== Helper Functions ==============

def _validate_csv_file():
    """Validate that a CSV file was provided."""
    if 'file' not in request.files:
        return error_response('No file provided', 400)

    file = request.files['file']
    if not file or not file.filename or not file.filename.endswith('.csv'):
        return error_response('Please provide a valid CSV file', 400)

    return None


def _read_csv_content():
    """Read and decode CSV content from the request file."""
    try:
        file = request.files['file']
        content = file.read().decode('utf-8-sig')
        return content, None
    except Exception as e:
        return None, error_response(f'Failed to parse CSV: {str(e)}', 400)


def _get_company_id(current_user: User) -> int:
    """Get the company ID for the import operation."""
    if current_user.role.name == 'super_admin':
        return request.form.get('company_id') or current_user.company_id
    return current_user.company_id
