"""
User Routes Package

This module registers all route blueprints for the user module.
"""
from flask import Blueprint

# Create blueprints
user_bp = Blueprint('user', __name__)
auth_bp = Blueprint('auth', __name__)

# Import routes to register them with blueprints
from . import auth_routes  # noqa: E402, F401
from . import user_routes  # noqa: E402, F401

__all__ = ['user_bp', 'auth_bp']
