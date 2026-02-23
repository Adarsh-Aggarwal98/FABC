"""
User Module

This module contains the user functionality including:
- Authentication (login, logout, 2FA, password reset)
- User management (CRUD, profiles, roles)
- Client notes
- User import/export

Architecture:
- models/       - SQLAlchemy ORM entities
- repositories/ - Data access layer
- usecases/     - Business logic orchestration
- schemas/      - Request/response validation
- routes/       - HTTP controllers (thin)
"""

# Import blueprints from routes package
from .routes import user_bp, auth_bp

# Re-export for backward compatibility
__all__ = ['user_bp', 'auth_bp']
