"""
Analytics module routes - Backward compatibility layer

This file is kept for backward compatibility.
Import from app.modules.analytics.routes instead.
"""
from .routes import (
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
