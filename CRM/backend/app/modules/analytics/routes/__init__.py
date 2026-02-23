"""
Analytics routes module

This module contains the API route handlers for analytics endpoints.
"""
from .analytics_routes import (
    get_dashboard_metrics,
    get_bottlenecks,
    get_accountant_workload,
    get_revenue_by_client,
    get_revenue_by_service,
    get_lodgement_summary,
)

__all__ = [
    'get_dashboard_metrics',
    'get_bottlenecks',
    'get_accountant_workload',
    'get_revenue_by_client',
    'get_revenue_by_service',
    'get_lodgement_summary',
]
