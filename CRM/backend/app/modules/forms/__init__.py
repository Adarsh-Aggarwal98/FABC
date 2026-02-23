"""
Forms Module
============

This module provides dynamic form management functionality for the CRM.
Forms can be customized per company with various question types.

Clean Architecture Structure:
----------------------------
- models/         - Database models (Form, FormQuestion, FormResponse)
- repositories/   - Data access layer
- usecases/       - Business logic layer
- schemas/        - Request/response validation
- routes/         - HTTP endpoints

Backward Compatibility:
----------------------
This module maintains backward compatibility by re-exporting all entities
from their original locations. Existing imports will continue to work.
"""
from flask import Blueprint

# Create the blueprint
forms_bp = Blueprint('forms', __name__)

# Import routes to register them with the blueprint
from app.modules.forms.routes import form_routes  # noqa: E402, F401
