"""
Forms Use Cases - Backward Compatibility Layer
==============================================

This file provides backward compatibility for imports from the old flat structure.
All use cases have been moved to the usecases/ folder.

Usage:
    # Old import style (still works):
    from app.modules.forms.usecases import CreateFormUseCase, GetFormUseCase, ...

    # New recommended import style:
    from app.modules.forms.usecases import CreateFormUseCase, GetFormUseCase, ...
    # or
    from app.modules.forms.usecases.form_usecases import CreateFormUseCase
"""
# Re-export all use cases from the new location for backward compatibility

# Form CRUD Use Cases
from app.modules.forms.usecases.form_usecases import (
    CreateFormUseCase,
    UpdateFormUseCase,
    DeleteFormUseCase,
    GetFormUseCase,
    ListFormsUseCase,
)

# Question Use Cases
from app.modules.forms.usecases.question_usecases import (
    AddQuestionUseCase,
    UpdateQuestionUseCase,
    DeleteQuestionUseCase,
    ReorderQuestionsUseCase,
)

# Response Use Cases
from app.modules.forms.usecases.response_usecases import (
    SubmitFormResponseUseCase,
    GetFormResponseUseCase,
    ListFormResponsesUseCase,
)

# Company Form Use Cases
from app.modules.forms.usecases.company_form_usecases import (
    ListDefaultFormsUseCase,
    CloneFormUseCase,
    CreateCompanyFormUseCase,
    UpdateFormStatusUseCase,
    ListCompanyFormsUseCase,
    DeleteCompanyFormUseCase,
)

__all__ = [
    # Form CRUD
    'CreateFormUseCase',
    'UpdateFormUseCase',
    'DeleteFormUseCase',
    'GetFormUseCase',
    'ListFormsUseCase',
    # Questions
    'AddQuestionUseCase',
    'UpdateQuestionUseCase',
    'DeleteQuestionUseCase',
    'ReorderQuestionsUseCase',
    # Responses
    'SubmitFormResponseUseCase',
    'GetFormResponseUseCase',
    'ListFormResponsesUseCase',
    # Company Forms
    'ListDefaultFormsUseCase',
    'CloneFormUseCase',
    'CreateCompanyFormUseCase',
    'UpdateFormStatusUseCase',
    'ListCompanyFormsUseCase',
    'DeleteCompanyFormUseCase',
]
