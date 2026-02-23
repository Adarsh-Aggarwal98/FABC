"""
Analytics Module Routes - Business Intelligence API Endpoints

This module provides REST API endpoints for analytics and reporting,
including dashboard metrics, workload analysis, and revenue breakdowns.

Endpoints:
---------
GET /api/analytics/dashboard
    Get dashboard metrics (request counts by status, trends).
    Required role: Accountant or higher

GET /api/analytics/bottlenecks
    Get bottleneck summary (requests stuck in each status).
    Required role: Accountant or higher

GET /api/analytics/workload
    Get accountant workload statistics (assignments per accountant).
    Required role: Accountant or higher

GET /api/analytics/revenue/by-client
    Get revenue breakdown by client (admin only).
    Query params: date_from, date_to
    Required role: Admin or higher

GET /api/analytics/revenue/by-service
    Get revenue breakdown by service type (admin only).
    Query params: date_from, date_to
    Required role: Admin or higher

GET /api/analytics/lodgement-summary
    Get lodgement/completion summary over time.
    Query params: period (monthly, quarterly, yearly)
    Required role: Admin or higher

Security Notes:
--------------
- Super admin can view analytics for any company using company_id param
- Other users are scoped to their own company
"""
import logging
from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required

from app.common.responses import success_response, error_response
from app.common.decorators import admin_required, accountant_required, get_current_user
from app.modules.analytics import analytics_bp
from app.modules.analytics.services import AnalyticsService

# Module-level logger
logger = logging.getLogger(__name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@accountant_required
def get_dashboard_metrics():
    """
    Get dashboard metrics.

    Returns request counts by status, recent trends, and key
    performance indicators for the company dashboard.
    """
    user = get_current_user()
    logger.info(f"GET /analytics/dashboard - Metrics request by user_id={user.id}")

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        logger.warning("Dashboard metrics requested without company_id")
        return error_response('Company ID required', 400)

    logger.debug(f"Fetching dashboard metrics for company_id={company_id}")
    metrics = AnalyticsService.get_dashboard_metrics(company_id)
    logger.info(f"Dashboard metrics retrieved for company_id={company_id}")
    return success_response(metrics)


@analytics_bp.route('/bottlenecks', methods=['GET'])
@jwt_required()
@accountant_required
def get_bottlenecks():
    """Get bottleneck summary"""
    user = get_current_user()

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    summary = AnalyticsService.get_bottleneck_summary(company_id)
    return success_response(summary)


@analytics_bp.route('/workload', methods=['GET'])
@jwt_required()
@accountant_required
def get_accountant_workload():
    """Get accountant workload statistics"""
    user = get_current_user()

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    workload = AnalyticsService.get_accountant_workload(company_id)
    return success_response({'accountants': workload})


@analytics_bp.route('/revenue/by-client', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_by_client():
    """Get revenue breakdown by client"""
    user = get_current_user()

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    # Parse dates
    date_from = None
    date_to = None
    if request.args.get('date_from'):
        try:
            date_from = datetime.fromisoformat(request.args.get('date_from'))
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            date_to = datetime.fromisoformat(request.args.get('date_to'))
        except ValueError:
            pass

    revenue = AnalyticsService.get_revenue_by_client(company_id, date_from, date_to)
    return success_response({'clients': revenue})


@analytics_bp.route('/revenue/by-service', methods=['GET'])
@jwt_required()
@admin_required
def get_revenue_by_service():
    """Get revenue breakdown by service type"""
    user = get_current_user()

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        return error_response('Company ID required', 400)

    # Parse dates
    date_from = None
    date_to = None
    if request.args.get('date_from'):
        try:
            date_from = datetime.fromisoformat(request.args.get('date_from'))
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            date_to = datetime.fromisoformat(request.args.get('date_to'))
        except ValueError:
            pass

    revenue = AnalyticsService.get_revenue_by_service(company_id, date_from, date_to)
    return success_response({'services': revenue})


@analytics_bp.route('/lodgement-summary', methods=['GET'])
@jwt_required()
@admin_required
def get_lodgement_summary():
    """Get lodgement/completion summary over time"""
    user = get_current_user()

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id
    period = request.args.get('period', 'monthly')

    if not company_id:
        return error_response('Company ID required', 400)

    if period not in ['monthly', 'quarterly', 'yearly']:
        return error_response('Invalid period. Use monthly, quarterly, or yearly', 400)

    summary = AnalyticsService.get_lodgement_summary(company_id, period)
    return success_response(summary)


@analytics_bp.route('/admin-dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_dashboard():
    """
    Get comprehensive admin dashboard metrics for client/user activity.

    Query params:
    - client_id (optional): Filter by specific client user
    - client_entity_id (optional): Filter by specific client entity
    - date_from (optional): Start date filter (ISO format)
    - date_to (optional): End date filter (ISO format)
    - company_id (optional): For super_admin to filter by company

    Returns summary stats, per-client breakdown, and per-request details.
    """
    user = get_current_user()
    logger.info(f"GET /analytics/admin-dashboard - Request by user_id={user.id}")

    company_id = request.args.get('company_id') if user.role.name == 'super_admin' else user.company_id

    if not company_id:
        logger.warning("Admin dashboard requested without company_id")
        return error_response('Company ID required', 400)

    # Parse optional filters
    client_id = request.args.get('client_id')
    client_entity_id = request.args.get('client_entity_id')

    date_from = None
    date_to = None
    if request.args.get('date_from'):
        try:
            date_from = datetime.fromisoformat(request.args.get('date_from'))
        except ValueError:
            pass
    if request.args.get('date_to'):
        try:
            date_to = datetime.fromisoformat(request.args.get('date_to'))
        except ValueError:
            pass

    logger.debug(f"Fetching admin dashboard for company_id={company_id}, client_id={client_id}")

    metrics = AnalyticsService.get_admin_dashboard_metrics(
        company_id=company_id,
        client_id=client_id,
        client_entity_id=client_entity_id,
        date_from=date_from,
        date_to=date_to
    )

    logger.info(f"Admin dashboard metrics retrieved for company_id={company_id}")
    return success_response(metrics)
