"""
Forms Repositories - Backward Compatibility Layer
==================================================

This file provides backward compatibility for imports from the old flat structure.
All repositories have been moved to the repositories/ folder.

Usage:
    # Old import style (still works):
    from app.modules.forms.repositories import FormRepository, FormQuestionRepository, FormResponseRepository

    # New recommended import style:
    from app.modules.forms.repositories import FormRepository, FormQuestionRepository, FormResponseRepository
    # or
    from app.modules.forms.repositories.form_repository import FormRepository
"""
# Re-export all repositories from the new location for backward compatibility
from app.modules.forms.repositories.form_repository import FormRepository
from app.modules.forms.repositories.form_question_repository import FormQuestionRepository
from app.modules.forms.repositories.form_response_repository import FormResponseRepository

__all__ = [
    'FormRepository',
    'FormQuestionRepository',
    'FormResponseRepository',
]
