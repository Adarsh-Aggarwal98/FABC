"""
Forms Models - Backward Compatibility Layer
============================================

This file provides backward compatibility for imports from the old flat structure.
All models have been moved to the models/ folder.

Usage:
    # Old import style (still works):
    from app.modules.forms.models import Form, FormQuestion, FormResponse

    # New recommended import style:
    from app.modules.forms.models import Form, FormQuestion, FormResponse
    # or
    from app.modules.forms.models.form import Form
    from app.modules.forms.models.form_question import FormQuestion
    from app.modules.forms.models.form_response import FormResponse
"""
# Re-export all models from the new location for backward compatibility
from app.modules.forms.models.form import Form
from app.modules.forms.models.form_question import FormQuestion
from app.modules.forms.models.form_response import FormResponse

__all__ = [
    'Form',
    'FormQuestion',
    'FormResponse',
]
