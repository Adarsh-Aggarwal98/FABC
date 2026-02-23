"""
Forms Use Cases Package
=======================

This package contains all use case classes for the forms module.
Use cases implement business logic following CQRS pattern.

Use Case Categories:
------------------
Form Management:
    - CreateFormUseCase: Create new system form
    - UpdateFormUseCase: Update form details
    - DeleteFormUseCase: Delete form
    - GetFormUseCase: Get single form
    - ListFormsUseCase: List forms with pagination

Company Forms:
    - CreateCompanyFormUseCase: Create company-specific form
    - CloneFormUseCase: Clone system form for company
    - ListCompanyFormsUseCase: List forms available to company
    - ListDefaultFormsUseCase: List system forms for cloning
    - UpdateFormStatusUseCase: Publish/archive form
    - DeleteCompanyFormUseCase: Delete company form

Questions:
    - AddQuestionUseCase: Add question to form
    - UpdateQuestionUseCase: Update question
    - DeleteQuestionUseCase: Delete question
    - ReorderQuestionsUseCase: Change question order

Responses:
    - SubmitFormResponseUseCase: Submit form answers
    - GetFormResponseUseCase: Get single response
    - ListFormResponsesUseCase: List responses
"""

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
