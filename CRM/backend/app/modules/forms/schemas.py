"""
Forms Schemas - Backward Compatibility Layer
=============================================

This file provides backward compatibility for imports from the old flat structure.
All schemas have been moved to the schemas/ folder.

Usage:
    # Old import style (still works):
    from app.modules.forms.schemas import CreateFormSchema, QuestionSchema, ...

    # New recommended import style:
    from app.modules.forms.schemas import CreateFormSchema, QuestionSchema, ...
    # or
    from app.modules.forms.schemas.form_schemas import CreateFormSchema
"""
# Re-export all schemas from the new location for backward compatibility
from app.modules.forms.schemas.question_schemas import (
    QuestionSchema,
    AddQuestionSchema,
    UpdateQuestionSchema,
    ReorderQuestionsSchema,
)

from app.modules.forms.schemas.form_schemas import (
    CreateFormSchema,
    UpdateFormSchema,
    CloneFormSchema,
    UpdateFormStatusSchema,
    ListDefaultFormsSchema,
)

from app.modules.forms.schemas.response_schemas import (
    SubmitResponseSchema,
    FormResponseSchema,
)

__all__ = [
    # Question schemas
    'QuestionSchema',
    'AddQuestionSchema',
    'UpdateQuestionSchema',
    'ReorderQuestionsSchema',
    # Form schemas
    'CreateFormSchema',
    'UpdateFormSchema',
    'CloneFormSchema',
    'UpdateFormStatusSchema',
    'ListDefaultFormsSchema',
    # Response schemas
    'SubmitResponseSchema',
    'FormResponseSchema',
]
