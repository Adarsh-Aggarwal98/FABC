"""
Forms Schemas Package
=====================

This package contains all validation schema classes for the forms module.
Schemas handle request/response validation using Marshmallow.
"""
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
