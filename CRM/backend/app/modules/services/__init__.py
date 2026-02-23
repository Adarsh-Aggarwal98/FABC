"""
Services Module

This module contains the services functionality including:
- Service catalog management
- Service request workflow
- Queries/messaging
- Invoicing
- Analytics and reporting

Architecture:
- models/       - SQLAlchemy ORM entities
- repositories/ - Data access layer
- usecases/     - Business logic orchestration
- schemas/      - Request/response validation
- routes/       - HTTP controllers (thin)
"""

# Import blueprints from routes package
from .routes import services_bp, requests_bp, workflow_bp, renewals_bp, status_bp, invoices_bp, task_bp, client_pricing_bp

# Re-export for backward compatibility
__all__ = ['services_bp', 'requests_bp', 'workflow_bp', 'renewals_bp', 'status_bp', 'invoices_bp', 'task_bp', 'client_pricing_bp']
