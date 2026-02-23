"""
Analytics Routes - Thin Controllers for analytics and reporting

These routes handle HTTP concerns for analytics operations.
"""
from flask import request, Response, current_app
from flask_jwt_extended import jwt_required
from datetime import date, timedelta, datetime
from decimal import Decimal

from . import requests_bp
from app.modules.services.models import (
    ServiceRequest, RequestStateHistory, Service
)
from app.modules.user.models import User
from app.common.decorators import admin_required, accountant_required, get_current_user
from app.common.responses import success_response, error_response


# ============== State Duration Analytics ==============

@requests_bp.route('/analytics/state-durations', methods=['GET'])
@jwt_required()
@admin_required
def get_state_duration_analytics():
    """Get analytics on average time spent in each state"""
    current_user = get_current_user()
    days = request.args.get('days', 30, type=int)
    company_id = request.args.get('company_id')

    # Non-super-admins can only see their own company's data
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id

    results = RequestStateHistory.get_average_state_durations(company_id, days)

    analytics = []
    for row in results:
        analytics.append({
            'state': row.to_state,
            'transition_count': row.count,
            'avg_duration_seconds': float(row.avg_duration) if row.avg_duration else 0,
            'avg_duration_formatted': RequestStateHistory._format_duration(int(row.avg_duration)) if row.avg_duration else None,
            'min_duration_seconds': row.min_duration,
            'max_duration_seconds': row.max_duration,
        })

    return success_response({
        'analytics': analytics,
        'period_days': days,
        'company_id': company_id
    })


# ============== Overdue Requests ==============

@requests_bp.route('/analytics/overdue', methods=['GET'])
@jwt_required()
@admin_required
def get_overdue_requests():
    """Get list of overdue requests (past deadline)"""
    current_user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Build query for overdue requests
    query = ServiceRequest.query.filter(
        ServiceRequest.deadline_date < date.today(),
        ServiceRequest.status != ServiceRequest.STATUS_COMPLETED
    )

    # Filter by company for non-super-admins
    if current_user.role.name != 'super_admin':
        query = query.join(User, ServiceRequest.user_id == User.id)\
            .filter(User.company_id == current_user.company_id)

    # Order by deadline (oldest first - most overdue)
    query = query.order_by(ServiceRequest.deadline_date.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response({
        'requests': [r.to_dict() for r in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


# ============== Deadline Summary ==============

@requests_bp.route('/analytics/deadline-summary', methods=['GET'])
@jwt_required()
@admin_required
def get_deadline_summary():
    """Get summary of requests by deadline status"""
    current_user = get_current_user()
    today = date.today()
    week_from_now = today + timedelta(days=7)

    # Base query
    base_query = ServiceRequest.query.filter(
        ServiceRequest.status != ServiceRequest.STATUS_COMPLETED
    )

    # Filter by company for non-super-admins
    if current_user.role.name != 'super_admin':
        base_query = base_query.join(User, ServiceRequest.user_id == User.id)\
            .filter(User.company_id == current_user.company_id)

    # Count overdue
    overdue_count = base_query.filter(
        ServiceRequest.deadline_date < today,
        ServiceRequest.deadline_date.isnot(None)
    ).count()

    # Count due this week
    due_this_week_count = base_query.filter(
        ServiceRequest.deadline_date >= today,
        ServiceRequest.deadline_date <= week_from_now
    ).count()

    # Count no deadline set
    no_deadline_count = base_query.filter(
        ServiceRequest.deadline_date.is_(None)
    ).count()

    # Count on track (deadline in future, more than a week out)
    on_track_count = base_query.filter(
        ServiceRequest.deadline_date > week_from_now
    ).count()

    return success_response({
        'summary': {
            'overdue': overdue_count,
            'due_this_week': due_this_week_count,
            'on_track': on_track_count,
            'no_deadline': no_deadline_count
        },
        'as_of': today.isoformat()
    })


# ============== Revenue vs Cost Analytics ==============

@requests_bp.route('/analytics/revenue-cost', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_cost_analytics():
    """Get revenue vs cost analytics with filtering options"""
    current_user = get_current_user()

    # Parse query params
    period = request.args.get('period', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    service_id = request.args.get('service_id', type=int)
    category = request.args.get('category')
    group_by = request.args.get('group_by', 'month')
    company_id = request.args.get('company_id')

    # Calculate date range
    today = datetime.utcnow().date()
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        period_days = {'day': 1, 'week': 7, 'month': 30, 'quarter': 90, 'year': 365}
        days = period_days.get(period, 30)
        start_date = today - timedelta(days=days)
        end_date = today

    # Base query - completed requests with invoice amount
    base_query = ServiceRequest.query.filter(
        ServiceRequest.invoice_amount.isnot(None),
        ServiceRequest.invoice_amount > 0,
        ServiceRequest.completed_at >= start_date,
        ServiceRequest.completed_at <= end_date
    )

    # Apply company filter
    if current_user.role.name != 'super_admin':
        company_id = current_user.company_id
    if company_id:
        base_query = base_query.join(User, ServiceRequest.user_id == User.id)\
            .filter(User.company_id == company_id)

    # Apply service filter
    if service_id:
        base_query = base_query.filter(ServiceRequest.service_id == service_id)

    # Apply category filter
    if category:
        base_query = base_query.join(Service, ServiceRequest.service_id == Service.id)\
            .filter(Service.cost_category == category)

    # Get all matching requests
    requests_data = base_query.all()

    # Calculate totals
    total_revenue = Decimal('0')
    total_cost = Decimal('0')
    total_estimated_cost = Decimal('0')

    for req in requests_data:
        if req.invoice_amount:
            total_revenue += req.invoice_amount
        if req.actual_cost:
            total_cost += req.actual_cost
        else:
            if req.service and req.service.cost_percentage and req.invoice_amount:
                estimated = req.invoice_amount * (req.service.cost_percentage / 100)
                total_estimated_cost += estimated

    total_all_cost = total_cost + total_estimated_cost
    profit = total_revenue - total_all_cost
    profit_margin = (float(profit) / float(total_revenue) * 100) if total_revenue > 0 else 0

    # Group by analysis
    grouped_data = _group_analytics_data(requests_data, group_by)

    return success_response({
        'summary': {
            'total_revenue': float(total_revenue),
            'total_actual_cost': float(total_cost),
            'total_estimated_cost': float(total_estimated_cost),
            'total_cost': float(total_all_cost),
            'profit': float(profit),
            'profit_margin': round(profit_margin, 2),
            'job_count': len(requests_data)
        },
        'grouped_by': group_by,
        'data': grouped_data,
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    })


def _group_analytics_data(requests_data, group_by):
    """Group analytics data by specified dimension"""
    grouped_data = []

    if group_by == 'service':
        service_stats = {}
        for req in requests_data:
            service_name = req.service.name if req.service else 'Unknown'
            if service_name not in service_stats:
                service_stats[service_name] = {
                    'name': service_name, 'revenue': Decimal('0'),
                    'cost': Decimal('0'), 'count': 0
                }
            service_stats[service_name]['revenue'] += req.invoice_amount or Decimal('0')
            if req.actual_cost:
                service_stats[service_name]['cost'] += req.actual_cost
            elif req.service and req.service.cost_percentage and req.invoice_amount:
                service_stats[service_name]['cost'] += req.invoice_amount * (req.service.cost_percentage / 100)
            service_stats[service_name]['count'] += 1

        for name, stats in service_stats.items():
            stats['profit'] = float(stats['revenue'] - stats['cost'])
            stats['profit_margin'] = (stats['profit'] / float(stats['revenue']) * 100) if stats['revenue'] > 0 else 0
            stats['revenue'] = float(stats['revenue'])
            stats['cost'] = float(stats['cost'])
            grouped_data.append(stats)

    elif group_by == 'month':
        month_stats = {}
        for req in requests_data:
            if req.completed_at:
                month_key = req.completed_at.strftime('%Y-%m')
                if month_key not in month_stats:
                    month_stats[month_key] = {
                        'month': month_key, 'revenue': Decimal('0'),
                        'cost': Decimal('0'), 'count': 0
                    }
                month_stats[month_key]['revenue'] += req.invoice_amount or Decimal('0')
                if req.actual_cost:
                    month_stats[month_key]['cost'] += req.actual_cost
                elif req.service and req.service.cost_percentage and req.invoice_amount:
                    month_stats[month_key]['cost'] += req.invoice_amount * (req.service.cost_percentage / 100)
                month_stats[month_key]['count'] += 1

        for month, stats in sorted(month_stats.items()):
            stats['profit'] = float(stats['revenue'] - stats['cost'])
            stats['profit_margin'] = (stats['profit'] / float(stats['revenue']) * 100) if stats['revenue'] > 0 else 0
            stats['revenue'] = float(stats['revenue'])
            stats['cost'] = float(stats['cost'])
            grouped_data.append(stats)

    elif group_by == 'accountant':
        accountant_stats = {}
        for req in requests_data:
            accountant_name = req.assigned_accountant.full_name if req.assigned_accountant else 'Unassigned'
            if accountant_name not in accountant_stats:
                accountant_stats[accountant_name] = {
                    'accountant': accountant_name, 'revenue': Decimal('0'),
                    'cost': Decimal('0'), 'count': 0
                }
            accountant_stats[accountant_name]['revenue'] += req.invoice_amount or Decimal('0')
            if req.actual_cost:
                accountant_stats[accountant_name]['cost'] += req.actual_cost
            elif req.service and req.service.cost_percentage and req.invoice_amount:
                accountant_stats[accountant_name]['cost'] += req.invoice_amount * (req.service.cost_percentage / 100)
            accountant_stats[accountant_name]['count'] += 1

        for name, stats in accountant_stats.items():
            stats['profit'] = float(stats['revenue'] - stats['cost'])
            stats['profit_margin'] = (stats['profit'] / float(stats['revenue']) * 100) if stats['revenue'] > 0 else 0
            stats['revenue'] = float(stats['revenue'])
            stats['cost'] = float(stats['cost'])
            grouped_data.append(stats)

    return grouped_data


# ============== Export Routes ==============

@requests_bp.route('/export', methods=['GET'])
@jwt_required()
@admin_required
def export_requests():
    """Export service requests to CSV or Excel"""
    from app.common.export import generate_csv, generate_excel, SERVICE_REQUEST_EXPORT_COLUMNS

    format_type = request.args.get('format', 'csv')
    status_filter = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    current_user = get_current_user()

    # Build query
    query = ServiceRequest.query.join(User, ServiceRequest.user_id == User.id)

    if current_user.role.name != 'super_admin':
        query = query.filter(User.company_id == current_user.company_id)

    if status_filter:
        query = query.filter(ServiceRequest.status == status_filter)

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(ServiceRequest.created_at >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(ServiceRequest.created_at <= to_date)
        except ValueError:
            pass

    requests_list = query.order_by(ServiceRequest.created_at.desc()).all()
    data = [r.to_dict(include_user=True, include_accountant=True) for r in requests_list]

    filename = f'requests_export_{status_filter or "all"}'

    if format_type == 'excel':
        return generate_excel(data, SERVICE_REQUEST_EXPORT_COLUMNS, filename)
    return generate_csv(data, SERVICE_REQUEST_EXPORT_COLUMNS, filename)


# ============== Invoice PDF Routes ==============

@requests_bp.route('/<request_id>/invoice/pdf', methods=['GET'])
@jwt_required()
def get_invoice_pdf(request_id):
    """Generate and download invoice PDF for a service request"""
    from app.modules.services.invoice_service import InvoicePDFService
    from app.modules.company.models import Company

    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 401)

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return error_response('Service request not found', 404)

    # Check access
    is_super_admin = current_user.role.name == 'super_admin'
    is_owner = service_request.user_id == current_user.id
    is_staff = current_user.role.name in ['admin', 'accountant'] and current_user.company_id == service_request.user.company_id

    if not (is_super_admin or is_owner or is_staff):
        return error_response('Access denied', 403)

    if not service_request.invoice_raised:
        return error_response('Invoice has not been raised for this request', 400)

    company = Company.query.get(current_user.company_id) if current_user.company_id else None

    try:
        pdf_bytes = InvoicePDFService.generate_invoice_pdf(service_request, company)
        filename = InvoicePDFService.get_invoice_filename(service_request, company)

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
    except Exception as e:
        current_app.logger.error(f'Failed to generate invoice PDF: {str(e)}')
        return error_response('Failed to generate invoice PDF', 500)


@requests_bp.route('/<request_id>/invoice/preview', methods=['GET'])
@jwt_required()
def preview_invoice_pdf(request_id):
    """Preview invoice PDF in browser (inline display)"""
    from app.modules.services.invoice_service import InvoicePDFService
    from app.modules.company.models import Company

    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 401)

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return error_response('Service request not found', 404)

    is_super_admin = current_user.role.name == 'super_admin'
    is_owner = service_request.user_id == current_user.id
    is_staff = current_user.role.name in ['admin', 'accountant'] and current_user.company_id == service_request.user.company_id

    if not (is_super_admin or is_owner or is_staff):
        return error_response('Access denied', 403)

    if not service_request.invoice_raised:
        return error_response('Invoice has not been raised for this request', 400)

    company = Company.query.get(current_user.company_id) if current_user.company_id else None

    try:
        pdf_bytes = InvoicePDFService.generate_invoice_pdf(service_request, company)
        filename = InvoicePDFService.get_invoice_filename(service_request, company)

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
    except Exception as e:
        current_app.logger.error(f'Failed to generate invoice PDF: {str(e)}')
        return error_response('Failed to generate invoice PDF', 500)


@requests_bp.route('/invoice/sample-preview', methods=['GET'])
@jwt_required()
def sample_invoice_preview():
    """Generate a sample invoice PDF for preview (using dummy data)"""
    from app.modules.services.invoice_service import InvoicePDFService
    from app.modules.company.models import Company

    current_user = get_current_user()
    if not current_user:
        return error_response('User not found', 401)

    if current_user.role.name not in ['super_admin', 'admin']:
        return error_response('Access denied', 403)

    company = Company.query.get(current_user.company_id) if current_user.company_id else None

    try:
        pdf_bytes = InvoicePDFService.generate_sample_invoice_pdf(company, current_user)
        filename = "sample-invoice.pdf"

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
    except Exception as e:
        current_app.logger.error(f'Failed to generate sample invoice PDF: {str(e)}')
        return error_response(f'Failed to generate sample invoice PDF: {str(e)}', 500)
