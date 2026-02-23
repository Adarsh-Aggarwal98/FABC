"""
Analytics Module

This module provides analytics and reporting functionality for the application,
including dashboard metrics, workload analysis, and revenue breakdowns.

Clean Architecture Structure:
- services/: Business logic services (AnalyticsService)
- routes/: API route handlers

For backward compatibility, key exports are available at the module level:
- analytics_bp: The Flask Blueprint for analytics routes
- AnalyticsService: The main analytics service class
"""
from flask import Blueprint

# Create the blueprint first (before importing routes)
analytics_bp = Blueprint('analytics', __name__)

# Import routes to register them with the blueprint
from .routes import analytics_routes  # noqa: E402, F401

# Export AnalyticsService for backward compatibility
from .services import AnalyticsService  # noqa: E402

__all__ = ['analytics_bp', 'AnalyticsService']
