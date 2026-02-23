"""
FormQuestion Repository - Data Access Layer for FormQuestion entities
"""
from typing import List
from app.common.repository import BaseRepository
from app.extensions import db
from app.modules.forms.models.form_question import FormQuestion


class FormQuestionRepository(BaseRepository[FormQuestion]):
    """Repository for FormQuestion data access"""
    model = FormQuestion

    def get_by_form(self, form_id: int) -> List[FormQuestion]:
        """Get all questions for a form"""
        return FormQuestion.query.filter_by(form_id=form_id)\
            .order_by(FormQuestion.order).all()

    def get_max_order(self, form_id: int) -> int:
        """Get maximum order value for a form's questions"""
        result = db.session.query(db.func.max(FormQuestion.order))\
            .filter_by(form_id=form_id).scalar()
        return result or 0

    def reorder_questions(self, form_id: int, question_orders: list) -> None:
        """Reorder questions in a form"""
        for item in question_orders:
            question = FormQuestion.query.get(item['question_id'])
            if question and question.form_id == form_id:
                question.order = item['order']
