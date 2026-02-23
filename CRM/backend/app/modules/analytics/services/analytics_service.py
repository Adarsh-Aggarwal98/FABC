"""
Analytics module services
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, and_
from app.extensions import db


class AnalyticsService:
    """Service for generating analytics and reports"""

    @staticmethod
    def get_stuck_requests(company_id: str, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """Get requests that have been in the same status for too long"""
        from app.modules.services.models import ServiceRequest
        from app.modules.user.models import User

        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)

        requests = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.status.notin_(['completed']),
            ServiceRequest.updated_at < threshold_date
        ).order_by(ServiceRequest.updated_at.asc()).all()

        return [{
            'request': r.to_dict(),
            'days_stuck': (datetime.utcnow() - r.updated_at).days
        } for r in requests]

    @staticmethod
    def get_overdue_requests(company_id: str) -> List[Dict[str, Any]]:
        """Get requests with raised invoices that haven't been paid"""
        from app.modules.services.models import ServiceRequest
        from app.modules.user.models import User

        requests = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.invoice_raised == True,
            ServiceRequest.invoice_paid == False
        ).order_by(ServiceRequest.created_at.asc()).all()

        return [r.to_dict() for r in requests]

    @staticmethod
    def get_accountant_workload(company_id: str) -> List[Dict[str, Any]]:
        """Get workload statistics for each accountant"""
        from app.modules.services.models import ServiceRequest
        from app.modules.user.models import User, Role

        # Get all accountants in the company
        accountants = User.query.join(Role).filter(
            User.company_id == company_id,
            Role.name.in_(['accountant', 'admin'])
        ).all()

        result = []
        for accountant in accountants:
            # Count active assignments
            active_count = ServiceRequest.query.filter(
                ServiceRequest.assigned_accountant_id == accountant.id,
                ServiceRequest.status.notin_(['completed'])
            ).count()

            # Count completed this month
            first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            completed_count = ServiceRequest.query.filter(
                ServiceRequest.assigned_accountant_id == accountant.id,
                ServiceRequest.status == 'completed',
                ServiceRequest.completed_at >= first_of_month
            ).count()

            result.append({
                'accountant': {
                    'id': accountant.id,
                    'email': accountant.email,
                    'full_name': accountant.full_name
                },
                'active_requests': active_count,
                'completed_this_month': completed_count
            })

        return sorted(result, key=lambda x: x['active_requests'], reverse=True)

    @staticmethod
    def get_bottleneck_summary(company_id: str) -> Dict[str, Any]:
        """Get summary of all bottlenecks"""
        stuck = AnalyticsService.get_stuck_requests(company_id)
        overdue = AnalyticsService.get_overdue_requests(company_id)
        workload = AnalyticsService.get_accountant_workload(company_id)

        # Find overloaded accountants (more than 10 active requests)
        overloaded = [w for w in workload if w['active_requests'] > 10]

        return {
            'stuck_requests': {
                'count': len(stuck),
                'items': stuck[:5]  # Top 5
            },
            'unpaid_invoices': {
                'count': len(overdue),
                'items': overdue[:5]
            },
            'overloaded_accountants': {
                'count': len(overloaded),
                'items': overloaded
            }
        }

    @staticmethod
    def get_revenue_by_client(
        company_id: str,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get revenue breakdown by client"""
        from app.modules.services.models import ServiceRequest
        from app.modules.user.models import User

        query = db.session.query(
            User.id,
            User.email,
            User.first_name,
            User.last_name,
            func.sum(ServiceRequest.invoice_amount).label('total_revenue'),
            func.count(ServiceRequest.id).label('request_count')
        ).join(ServiceRequest, ServiceRequest.user_id == User.id).filter(
            User.company_id == company_id,
            ServiceRequest.invoice_paid == True
        )

        if date_from:
            query = query.filter(ServiceRequest.completed_at >= date_from)
        if date_to:
            query = query.filter(ServiceRequest.completed_at <= date_to)

        query = query.group_by(User.id, User.email, User.first_name, User.last_name)
        query = query.order_by(func.sum(ServiceRequest.invoice_amount).desc())

        results = query.all()

        return [{
            'client': {
                'id': r.id,
                'email': r.email,
                'full_name': f'{r.first_name or ""} {r.last_name or ""}'.strip() or r.email
            },
            'total_revenue': float(r.total_revenue) if r.total_revenue else 0,
            'request_count': r.request_count
        } for r in results]

    @staticmethod
    def get_revenue_by_service(
        company_id: str,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get revenue breakdown by service type"""
        from app.modules.services.models import ServiceRequest, Service
        from app.modules.user.models import User

        query = db.session.query(
            Service.id,
            Service.name,
            Service.category,
            func.sum(ServiceRequest.invoice_amount).label('total_revenue'),
            func.count(ServiceRequest.id).label('request_count')
        ).join(ServiceRequest, ServiceRequest.service_id == Service.id).join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.invoice_paid == True
        )

        if date_from:
            query = query.filter(ServiceRequest.completed_at >= date_from)
        if date_to:
            query = query.filter(ServiceRequest.completed_at <= date_to)

        query = query.group_by(Service.id, Service.name, Service.category)
        query = query.order_by(func.sum(ServiceRequest.invoice_amount).desc())

        results = query.all()

        return [{
            'service': {
                'id': r.id,
                'name': r.name,
                'category': r.category
            },
            'total_revenue': float(r.total_revenue) if r.total_revenue else 0,
            'request_count': r.request_count
        } for r in results]

    @staticmethod
    def get_lodgement_summary(
        company_id: str,
        period: str = 'monthly'  # monthly, quarterly, yearly
    ) -> Dict[str, Any]:
        """Get lodgement/completion statistics over time"""
        from app.modules.services.models import ServiceRequest
        from app.modules.user.models import User

        # Use strftime for SQLite compatibility (works with PostgreSQL too)
        if period == 'monthly':
            period_expr = func.strftime('%Y-%m', ServiceRequest.completed_at)
        elif period == 'quarterly':
            # For quarterly, extract year and quarter
            period_expr = func.strftime('%Y-Q', ServiceRequest.completed_at) + \
                         func.cast((func.cast(func.strftime('%m', ServiceRequest.completed_at), db.Integer) - 1) / 3 + 1, db.String)
        else:  # yearly
            period_expr = func.strftime('%Y', ServiceRequest.completed_at)

        query = db.session.query(
            period_expr.label('period'),
            func.count(ServiceRequest.id).label('completed_count'),
            func.sum(ServiceRequest.invoice_amount).label('total_revenue')
        ).join(User, ServiceRequest.user_id == User.id).filter(
            User.company_id == company_id,
            ServiceRequest.status == 'completed',
            ServiceRequest.completed_at.isnot(None)
        ).group_by(period_expr).order_by(period_expr)

        results = query.all()

        return {
            'period_type': period,
            'data': [{
                'period': r.period,
                'completed_count': r.completed_count,
                'total_revenue': float(r.total_revenue) if r.total_revenue else 0
            } for r in results]
        }

    @staticmethod
    def get_dashboard_metrics(company_id: str) -> Dict[str, Any]:
        """Get key metrics for dashboard"""
        from app.modules.services.models import ServiceRequest
        from app.modules.user.models import User, Role

        # Total clients
        client_count = User.query.join(Role).filter(
            User.company_id == company_id,
            Role.name == 'user'
        ).count()

        # Active requests - use explicit join condition (exclude drafts)
        active_requests = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.status.notin_(['completed', 'draft'])
        ).count()

        # Pending requests (not assigned)
        pending_requests = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.status == 'pending'
        ).count()

        # Completed this month
        first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_this_month = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.status == 'completed',
            ServiceRequest.completed_at >= first_of_month
        ).count()

        # Revenue this month
        revenue_this_month = db.session.query(
            func.sum(ServiceRequest.invoice_amount)
        ).join(User, ServiceRequest.user_id == User.id).filter(
            User.company_id == company_id,
            ServiceRequest.invoice_paid == True,
            ServiceRequest.completed_at >= first_of_month
        ).scalar() or 0

        # Status breakdown (exclude drafts)
        status_breakdown = db.session.query(
            ServiceRequest.status,
            func.count(ServiceRequest.id)
        ).join(User, ServiceRequest.user_id == User.id).filter(
            User.company_id == company_id,
            ServiceRequest.status != 'draft'
        ).group_by(ServiceRequest.status).all()

        return {
            'client_count': client_count,
            'active_requests': active_requests,
            'pending_requests': pending_requests,
            'completed_this_month': completed_this_month,
            'revenue_this_month': float(revenue_this_month),
            'status_breakdown': {status: count for status, count in status_breakdown}
        }

    @staticmethod
    def get_admin_dashboard_metrics(
        company_id: str,
        client_id: str = None,
        client_entity_id: str = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive admin dashboard metrics for client/user activity.

        Returns summary stats, per-client breakdown, and per-request details including:
        - Request counts and status breakdown
        - Revenue (from paid invoices)
        - Time spent (labor_hours + job note time entries)
        - Query counts
        """
        from app.modules.services.models import ServiceRequest, Service
        from app.modules.services.models.job_note import JobNote
        from app.modules.services.models.query import Query
        from app.modules.user.models import User, Role
        from app.modules.client_entity.models import ClientEntity

        # Base filters
        base_filters = [User.company_id == company_id]

        if client_id:
            base_filters.append(ServiceRequest.user_id == client_id)

        if client_entity_id:
            base_filters.append(ServiceRequest.client_entity_id == client_entity_id)

        if date_from:
            base_filters.append(ServiceRequest.created_at >= date_from)

        if date_to:
            base_filters.append(ServiceRequest.created_at <= date_to)

        # ============ SUMMARY METRICS ============

        # Total requests count
        total_requests = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(*base_filters).count()

        # Status breakdown
        status_query = db.session.query(
            ServiceRequest.status,
            func.count(ServiceRequest.id)
        ).join(User, ServiceRequest.user_id == User.id).filter(
            *base_filters
        ).group_by(ServiceRequest.status).all()

        status_breakdown = {status: count for status, count in status_query}

        # Total revenue (paid invoices only)
        total_revenue = db.session.query(
            func.sum(ServiceRequest.invoice_amount)
        ).join(User, ServiceRequest.user_id == User.id).filter(
            *base_filters,
            ServiceRequest.invoice_paid == True
        ).scalar() or 0

        # Total time spent from labor_hours
        labor_hours_total = db.session.query(
            func.sum(ServiceRequest.labor_hours)
        ).join(User, ServiceRequest.user_id == User.id).filter(
            *base_filters
        ).scalar() or 0

        # Additional time from job notes
        job_notes_time = db.session.query(
            func.sum(JobNote.time_spent_minutes)
        ).join(
            ServiceRequest, JobNote.service_request_id == ServiceRequest.id
        ).join(
            User, ServiceRequest.user_id == User.id
        ).filter(*base_filters).scalar() or 0

        total_time_spent_hours = float(labor_hours_total) + (job_notes_time / 60)

        # Total queries count
        total_queries = db.session.query(
            func.count(Query.id)
        ).join(
            ServiceRequest, Query.service_request_id == ServiceRequest.id
        ).join(
            User, ServiceRequest.user_id == User.id
        ).filter(*base_filters).scalar() or 0

        # ============ CLIENT BREAKDOWN ============

        # Get clients with their metrics
        client_query = db.session.query(
            User.id,
            User.email,
            User.first_name,
            User.last_name,
            func.count(ServiceRequest.id).label('request_count'),
            func.sum(
                db.case(
                    (ServiceRequest.invoice_paid == True, ServiceRequest.invoice_amount),
                    else_=0
                )
            ).label('total_revenue'),
            func.sum(ServiceRequest.labor_hours).label('labor_hours')
        ).join(
            ServiceRequest, ServiceRequest.user_id == User.id
        ).join(
            Role, User.role_id == Role.id
        ).filter(
            User.company_id == company_id,
            Role.name == 'user'
        )

        # Apply date filters for client query too
        if date_from:
            client_query = client_query.filter(ServiceRequest.created_at >= date_from)
        if date_to:
            client_query = client_query.filter(ServiceRequest.created_at <= date_to)

        client_query = client_query.group_by(
            User.id, User.email, User.first_name, User.last_name
        ).order_by(func.count(ServiceRequest.id).desc())

        client_results = client_query.all()

        clients = []
        for client in client_results:
            # Get entity count for this client
            entity_count = db.session.query(
                func.count(func.distinct(ServiceRequest.client_entity_id))
            ).filter(
                ServiceRequest.user_id == client.id,
                ServiceRequest.client_entity_id.isnot(None)
            ).scalar() or 0

            # Get query count for this client's requests
            query_count = db.session.query(
                func.count(Query.id)
            ).join(
                ServiceRequest, Query.service_request_id == ServiceRequest.id
            ).filter(ServiceRequest.user_id == client.id).scalar() or 0

            # Get job notes time for this client
            client_job_notes_time = db.session.query(
                func.sum(JobNote.time_spent_minutes)
            ).join(
                ServiceRequest, JobNote.service_request_id == ServiceRequest.id
            ).filter(ServiceRequest.user_id == client.id).scalar() or 0

            client_labor_hours = float(client.labor_hours) if client.labor_hours else 0
            client_total_time = client_labor_hours + (client_job_notes_time / 60)

            clients.append({
                'client_id': client.id,
                'client_name': f'{client.first_name or ""} {client.last_name or ""}'.strip() or client.email,
                'client_email': client.email,
                'entity_count': entity_count,
                'request_count': client.request_count,
                'total_revenue': float(client.total_revenue) if client.total_revenue else 0,
                'total_time_spent_hours': round(client_total_time, 2),
                'query_count': query_count
            })

        # ============ REQUEST DETAILS ============

        # Get individual request details
        requests_query = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).join(
            Service, ServiceRequest.service_id == Service.id
        ).filter(*base_filters).order_by(ServiceRequest.created_at.desc()).limit(100)

        requests_detail = []
        for req in requests_query.all():
            # Get query count for this request
            req_query_count = Query.query.filter_by(service_request_id=req.id).count()

            # Get job notes time for this request
            req_job_notes_time = db.session.query(
                func.sum(JobNote.time_spent_minutes)
            ).filter(JobNote.service_request_id == req.id).scalar() or 0

            req_labor_hours = float(req.labor_hours) if req.labor_hours else 0
            req_total_time = req_labor_hours + (req_job_notes_time / 60)

            requests_detail.append({
                'request_id': req.id,
                'request_number': req.request_number,
                'service_name': req.service.name if req.service else 'Unknown',
                'client_name': req.user.full_name if req.user else 'Unknown',
                'client_id': req.user_id,
                'client_entity_name': req.client_entity.name if req.client_entity else None,
                'status': req.status,
                'invoice_amount': float(req.invoice_amount) if req.invoice_amount else None,
                'invoice_paid': req.invoice_paid,
                'time_spent_hours': round(req_total_time, 2),
                'query_count': req_query_count,
                'created_at': req.created_at.isoformat() if req.created_at else None
            })

        return {
            'summary': {
                'total_requests': total_requests,
                'total_revenue': float(total_revenue),
                'total_time_spent_hours': round(total_time_spent_hours, 2),
                'total_queries': total_queries,
                'status_breakdown': status_breakdown
            },
            'clients': clients,
            'requests_detail': requests_detail
        }
