"""
Response Use Cases - Business Logic for Form Response operations
"""
import logging
from app.common.usecase import BaseCommandUseCase, BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.forms.models.form_response import FormResponse
from app.modules.forms.repositories.form_repository import FormRepository
from app.modules.forms.repositories.form_response_repository import FormResponseRepository

# Configure module-level logger
logger = logging.getLogger(__name__)


class SubmitFormResponseUseCase(BaseCommandUseCase):
    """
    Submit a response to a form.

    Business Rules:
    - All required questions must be answered
    - Validates response structure
    """

    def __init__(self):
        self.form_repo = FormRepository()
        self.response_repo = FormResponseRepository()

    def execute(self, form_id: int, user_id: str, responses: dict,
                service_request_id: str = None, partial: bool = False) -> UseCaseResult:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        # Validate required questions (skip when partial save by staff)
        if not partial:
            for question in form.questions:
                if question.is_required:
                    answer = responses.get(str(question.id))
                    if answer is None or answer == '' or (isinstance(answer, list) and len(answer) == 0):
                        return UseCaseResult.fail(
                            f'"{question.question_text}" is required',
                            'REQUIRED_FIELD'
                        )

        # Use create_with_snapshot to properly populate response_data field
        response = FormResponse.create_with_snapshot(
            form=form,
            user_id=user_id,
            answers=responses,
            service_request_id=service_request_id
        )
        self.response_repo.create(response)
        db.session.commit()

        return UseCaseResult.ok({'response': response.to_dict()})


class GetFormResponseUseCase(BaseQueryUseCase):
    """Get a specific form response"""

    def __init__(self):
        self.response_repo = FormResponseRepository()

    def execute(self, response_id: int, include_questions: bool = True) -> UseCaseResult:
        response = self.response_repo.get_by_id(response_id)
        if not response:
            return UseCaseResult.fail('Response not found', 'NOT_FOUND')

        return UseCaseResult.ok({'response': response.to_dict(include_questions=include_questions)})


class ListFormResponsesUseCase(BaseQueryUseCase):
    """List all responses for a form, optionally filtered by service request"""

    def __init__(self):
        self.response_repo = FormResponseRepository()

    def execute(self, form_id: int, page: int = 1, per_page: int = 20,
                service_request_id: str = None) -> UseCaseResult:
        # If service_request_id is provided, filter by it
        if service_request_id:
            responses = self.response_repo.get_by_service_request(service_request_id)
            # Filter by form_id as well
            responses = [r for r in responses if r.form_id == form_id]
            return UseCaseResult.ok({
                'responses': [r.to_dict(include_questions=True) for r in responses],
                'pagination': {
                    'page': 1,
                    'per_page': len(responses),
                    'total': len(responses),
                    'pages': 1
                }
            })

        pagination = self.response_repo.get_by_form_paginated(form_id, page, per_page)

        return UseCaseResult.ok({
            'responses': [r.to_dict(include_questions=True) for r in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
