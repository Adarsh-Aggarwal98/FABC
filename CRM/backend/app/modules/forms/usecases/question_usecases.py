"""
Question Use Cases - Business Logic for Form Question operations
"""
import logging
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.forms.models.form_question import FormQuestion
from app.modules.forms.repositories.form_repository import FormRepository
from app.modules.forms.repositories.form_question_repository import FormQuestionRepository

# Configure module-level logger
logger = logging.getLogger(__name__)


class AddQuestionUseCase(BaseCommandUseCase):
    """Add a question to a form"""

    def __init__(self):
        self.form_repo = FormRepository()
        self.question_repo = FormQuestionRepository()

    def execute(self, form_id: int, question_data: dict) -> UseCaseResult:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        # Validate question type
        if question_data['question_type'] not in FormQuestion.VALID_TYPES:
            return UseCaseResult.fail(
                f"Invalid question type: {question_data['question_type']}",
                'INVALID_TYPE'
            )

        # Get max order
        max_order = self.question_repo.get_max_order(form_id)

        question = FormQuestion(
            form_id=form_id,
            question_text=question_data['question_text'],
            question_type=question_data['question_type'],
            is_required=question_data.get('is_required', False),
            allow_attachment=question_data.get('allow_attachment', False),
            options=question_data.get('options'),
            validation_rules=question_data.get('validation_rules'),
            placeholder=question_data.get('placeholder'),
            help_text=question_data.get('help_text'),
            order=question_data.get('order', max_order + 1)
        )
        self.question_repo.create(question)
        db.session.commit()

        return UseCaseResult.ok({'question': question.to_dict()})


class UpdateQuestionUseCase(BaseCommandUseCase):
    """Update a question"""

    def __init__(self):
        self.question_repo = FormQuestionRepository()

    def execute(self, question_id: int, data: dict) -> UseCaseResult:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            return UseCaseResult.fail('Question not found', 'NOT_FOUND')

        updateable_fields = [
            'question_text', 'question_type', 'is_required', 'allow_attachment',
            'options', 'validation_rules', 'placeholder', 'help_text', 'order'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(question, field, data[field])

        db.session.commit()
        return UseCaseResult.ok({'question': question.to_dict()})


class DeleteQuestionUseCase(BaseCommandUseCase):
    """Delete a question"""

    def __init__(self):
        self.question_repo = FormQuestionRepository()

    def execute(self, question_id: int) -> UseCaseResult:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            return UseCaseResult.fail('Question not found', 'NOT_FOUND')

        self.question_repo.delete(question)
        db.session.commit()
        return UseCaseResult.ok({'message': 'Question deleted successfully'})


class ReorderQuestionsUseCase(BaseCommandUseCase):
    """Reorder questions in a form"""

    def __init__(self):
        self.form_repo = FormRepository()
        self.question_repo = FormQuestionRepository()

    def execute(self, form_id: int, question_orders: list) -> UseCaseResult:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        self.question_repo.reorder_questions(form_id, question_orders)
        db.session.commit()

        return UseCaseResult.ok({'form': form.to_dict()})
