"""
Renewal API Routes
Handles service renewal tracking and reminders
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.common.decorators import get_current_user, admin_required, accountant_required
from app.modules.services.services.renewal_service import RenewalService
from app.modules.services.models import ServiceRenewal, Service
from app.extensions import db
from datetime import date

renewals_bp = Blueprint('renewals', __name__)


def success_response(data=None, message=None, status_code=200):
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status_code


def error_response(error, status_code=400):
    return jsonify({'success': False, 'error': error}), status_code


@renewals_bp.route('', methods=['GET'])
@jwt_required()
@accountant_required
def list_renewals():
    """
    List upcoming renewals for the company.
    Query params:
    - days_ahead: Number of days to look ahead (default 30)
    - status: Filter by status (pending, reminded, completed, skipped)
    - service_id: Filter by service
    """
    current_user = get_current_user()

    days_ahead = request.args.get('days_ahead', 30, type=int)
    status_filter = request.args.get('status')
    service_id = request.args.get('service_id', type=int)

    # Get company_id - super admin sees all
    if current_user.role.name == 'super_admin':
        company_id = request.args.get('company_id')
        if not company_id:
            return error_response('company_id required for super admin', 400)
    else:
        company_id = current_user.company_id

    renewals = RenewalService.get_upcoming_renewals(
        company_id=company_id,
        days_ahead=days_ahead,
        status=status_filter
    )

    # Filter by service if specified
    if service_id:
        renewals = [r for r in renewals if r.service_id == service_id]

    return success_response({
        'renewals': [r.to_dict(include_user=True, include_service=True) for r in renewals],
        'total': len(renewals)
    })


@renewals_bp.route('/<int:renewal_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_renewal(renewal_id):
    """Get a specific renewal"""
    renewal = ServiceRenewal.query.get(renewal_id)
    if not renewal:
        return error_response('Renewal not found', 404)

    return success_response({
        'renewal': renewal.to_dict(include_user=True, include_service=True)
    })


@renewals_bp.route('/<int:renewal_id>/send-reminder', methods=['POST'])
@jwt_required()
@accountant_required
def send_manual_reminder(renewal_id):
    """Manually send a reminder for a renewal"""
    success = RenewalService.send_manual_reminder(renewal_id)

    if success:
        return success_response(message='Reminder sent successfully')
    else:
        return error_response('Failed to send reminder', 500)


@renewals_bp.route('/<int:renewal_id>/complete', methods=['POST'])
@jwt_required()
@accountant_required
def mark_complete(renewal_id):
    """Mark a renewal as completed and create next renewal"""
    request_id = request.json.get('request_id') if request.json else None

    new_renewal = RenewalService.mark_renewal_completed(renewal_id, request_id)

    if new_renewal:
        return success_response({
            'renewal': new_renewal.to_dict(include_user=True, include_service=True),
            'message': 'Renewal completed, next renewal created'
        })
    else:
        return error_response('Renewal not found', 404)


@renewals_bp.route('/<int:renewal_id>/skip', methods=['POST'])
@jwt_required()
@accountant_required
def skip_renewal(renewal_id):
    """Skip a renewal"""
    reason = request.json.get('reason') if request.json else None

    renewal = RenewalService.skip_renewal(renewal_id, reason)

    if renewal:
        return success_response({
            'renewal': renewal.to_dict(),
            'message': 'Renewal skipped'
        })
    else:
        return error_response('Renewal not found', 404)


@renewals_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_user_renewals(user_id):
    """Get all renewals for a specific user/client"""
    renewals = ServiceRenewal.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(ServiceRenewal.next_due_date).all()

    return success_response({
        'renewals': [r.to_dict(include_service=True) for r in renewals],
        'total': len(renewals)
    })


@renewals_bp.route('/service/<int:service_id>', methods=['GET'])
@jwt_required()
@accountant_required
def get_service_renewals(service_id):
    """Get all renewals for a specific service"""
    current_user = get_current_user()

    query = ServiceRenewal.query.filter_by(
        service_id=service_id,
        is_active=True
    )

    if current_user.role.name != 'super_admin':
        query = query.filter_by(company_id=current_user.company_id)

    renewals = query.order_by(ServiceRenewal.next_due_date).all()

    return success_response({
        'renewals': [r.to_dict(include_user=True) for r in renewals],
        'total': len(renewals)
    })


@renewals_bp.route('/process-reminders', methods=['POST'])
@jwt_required()
@admin_required
def trigger_reminder_processing():
    """
    Manually trigger the reminder processing job.
    Useful for testing or immediate processing.
    """
    from app.jobs.renewal_reminders import run_manual_reminder_check

    result = run_manual_reminder_check()

    return success_response({
        'result': result,
        'message': f'Processed {result["total"]} reminders, sent {result["sent"]}, failed {result["failed"]}'
    })


@renewals_bp.route('/create', methods=['POST'])
@jwt_required()
@accountant_required
def create_renewal():
    """
    Manually create a renewal for a user.
    Useful when onboarding existing clients.
    """
    data = request.json
    user_id = data.get('user_id')
    service_id = data.get('service_id')
    next_due_date = data.get('next_due_date')

    if not all([user_id, service_id, next_due_date]):
        return error_response('user_id, service_id, and next_due_date are required', 400)

    current_user = get_current_user()

    # Parse date
    try:
        due_date = date.fromisoformat(next_due_date)
    except ValueError:
        return error_response('Invalid date format. Use YYYY-MM-DD', 400)

    # Get service
    service = Service.query.get(service_id)
    if not service:
        return error_response('Service not found', 404)

    # Create renewal
    renewal = ServiceRenewal(
        user_id=user_id,
        service_id=service_id,
        company_id=current_user.company_id,
        next_due_date=due_date,
        status=ServiceRenewal.STATUS_PENDING
    )

    db.session.add(renewal)
    db.session.commit()

    return success_response({
        'renewal': renewal.to_dict(include_user=True, include_service=True)
    }, status_code=201)


@renewals_bp.route('/stats', methods=['GET'])
@jwt_required()
@accountant_required
def get_renewal_stats():
    """Get renewal statistics for dashboard"""
    current_user = get_current_user()

    if current_user.role.name == 'super_admin':
        company_id = request.args.get('company_id')
    else:
        company_id = current_user.company_id

    today = date.today()

    # Count by status
    base_query = ServiceRenewal.query.filter_by(company_id=company_id, is_active=True)

    # Overdue
    overdue = base_query.filter(
        ServiceRenewal.next_due_date < today,
        ServiceRenewal.status.in_([ServiceRenewal.STATUS_PENDING, ServiceRenewal.STATUS_REMINDED])
    ).count()

    # Due this week
    from datetime import timedelta
    week_end = today + timedelta(days=7)
    due_this_week = base_query.filter(
        ServiceRenewal.next_due_date >= today,
        ServiceRenewal.next_due_date <= week_end,
        ServiceRenewal.status.in_([ServiceRenewal.STATUS_PENDING, ServiceRenewal.STATUS_REMINDED])
    ).count()

    # Due this month
    month_end = today + timedelta(days=30)
    due_this_month = base_query.filter(
        ServiceRenewal.next_due_date >= today,
        ServiceRenewal.next_due_date <= month_end,
        ServiceRenewal.status.in_([ServiceRenewal.STATUS_PENDING, ServiceRenewal.STATUS_REMINDED])
    ).count()

    # Total active
    total_active = base_query.filter(
        ServiceRenewal.status.in_([ServiceRenewal.STATUS_PENDING, ServiceRenewal.STATUS_REMINDED])
    ).count()

    return success_response({
        'stats': {
            'overdue': overdue,
            'due_this_week': due_this_week,
            'due_this_month': due_this_month,
            'total_active': total_active
        }
    })
