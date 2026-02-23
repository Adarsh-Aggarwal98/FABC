"""
Form Use Cases - Business Logic for Form CRUD operations
"""
import logging
from app.common.usecase import BaseCommandUseCase, BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.forms.models.form import Form
from app.modules.forms.models.form_question import FormQuestion
from app.modules.forms.repositories.form_repository import FormRepository

# Configure module-level logger
logger = logging.getLogger(__name__)


class CreateFormUseCase(BaseCommandUseCase):
    """Create a new form with optional questions"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, name: str, form_type: str, created_by_id: str,
                description: str = None, questions: list = None) -> UseCaseResult:
        form = Form(
            name=name,
            description=description,
            form_type=form_type,
            created_by_id=created_by_id
        )
        self.form_repo.create(form)
        db.session.flush()  # Get the form ID

        if questions:
            for idx, q_data in enumerate(questions):
                question = FormQuestion(
                    form_id=form.id,
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    is_required=q_data.get('is_required', False),
                    allow_attachment=q_data.get('allow_attachment', False),
                    options=q_data.get('options'),
                    validation_rules=q_data.get('validation_rules'),
                    placeholder=q_data.get('placeholder'),
                    help_text=q_data.get('help_text'),
                    order=q_data.get('order', idx)
                )
                db.session.add(question)

        db.session.commit()
        return UseCaseResult.ok({'form': form.to_dict()})


class UpdateFormUseCase(BaseCommandUseCase):
    """Update form details"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_id: int, data: dict) -> UseCaseResult:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        if 'name' in data:
            form.name = data['name']
        if 'description' in data:
            form.description = data['description']
        if 'is_active' in data:
            form.is_active = data['is_active']

        db.session.commit()
        return UseCaseResult.ok({'form': form.to_dict()})


class DeleteFormUseCase(BaseCommandUseCase):
    """Delete a form and its questions"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_id: int) -> UseCaseResult:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        self.form_repo.delete(form)
        db.session.commit()
        return UseCaseResult.ok({'message': 'Form deleted successfully'})


class GetFormUseCase(BaseQueryUseCase):
    """Get a form by ID"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_id: int, include_questions: bool = True) -> UseCaseResult:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        return UseCaseResult.ok({'form': form.to_dict(include_questions=include_questions)})


class ListFormsUseCase(BaseQueryUseCase):
    """List all forms with pagination"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_type: str = None, active_only: bool = True,
                page: int = 1, per_page: int = 20) -> UseCaseResult:
        pagination = self.form_repo.get_forms_paginated(form_type, active_only, page, per_page)

        return UseCaseResult.ok({
            'forms': [f.to_dict(include_questions=False) for f in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
