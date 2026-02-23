from app.extensions import db
from app.modules.forms.models import Form, FormQuestion, FormResponse  # Works with both old and new structure
from app.common.exceptions import ValidationError, NotFoundError


class FormService:
    """Service for managing forms and questions"""

    @staticmethod
    def create_form(name, form_type, created_by, description=None, questions=None):
        """Create a new form with optional questions"""
        form = Form(
            name=name,
            description=description,
            form_type=form_type,
            created_by_id=created_by.id
        )
        db.session.add(form)
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
        return form

    @staticmethod
    def update_form(form_id, data):
        """Update form details"""
        form = Form.query.get(form_id)
        if not form:
            raise NotFoundError('Form not found')

        if 'name' in data:
            form.name = data['name']
        if 'description' in data:
            form.description = data['description']
        if 'is_active' in data:
            form.is_active = data['is_active']

        db.session.commit()
        return form

    @staticmethod
    def delete_form(form_id):
        """Delete a form and its questions"""
        form = Form.query.get(form_id)
        if not form:
            raise NotFoundError('Form not found')

        db.session.delete(form)
        db.session.commit()

    @staticmethod
    def add_question(form_id, question_data):
        """Add a question to a form"""
        form = Form.query.get(form_id)
        if not form:
            raise NotFoundError('Form not found')

        # Validate question type
        if question_data['question_type'] not in FormQuestion.VALID_TYPES:
            raise ValidationError(f"Invalid question type: {question_data['question_type']}")

        # Get max order
        max_order = db.session.query(db.func.max(FormQuestion.order)).filter_by(form_id=form_id).scalar() or 0

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
        db.session.add(question)
        db.session.commit()

        return question

    @staticmethod
    def update_question(question_id, data):
        """Update a question"""
        question = FormQuestion.query.get(question_id)
        if not question:
            raise NotFoundError('Question not found')

        updateable_fields = [
            'question_text', 'question_type', 'is_required', 'allow_attachment',
            'options', 'validation_rules', 'placeholder', 'help_text', 'order'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(question, field, data[field])

        db.session.commit()
        return question

    @staticmethod
    def delete_question(question_id):
        """Delete a question"""
        question = FormQuestion.query.get(question_id)
        if not question:
            raise NotFoundError('Question not found')

        db.session.delete(question)
        db.session.commit()

    @staticmethod
    def reorder_questions(form_id, question_orders):
        """Reorder questions in a form
        question_orders: [{question_id: 1, order: 0}, {question_id: 2, order: 1}, ...]
        """
        form = Form.query.get(form_id)
        if not form:
            raise NotFoundError('Form not found')

        for item in question_orders:
            question = FormQuestion.query.get(item['question_id'])
            if question and question.form_id == form_id:
                question.order = item['order']

        db.session.commit()
        return form

    @staticmethod
    def get_form(form_id):
        """Get a form by ID"""
        form = Form.query.get(form_id)
        if not form:
            raise NotFoundError('Form not found')
        return form

    @staticmethod
    def get_forms(form_type=None, active_only=True, page=1, per_page=20):
        """Get paginated list of forms"""
        query = Form.query

        if form_type:
            query = query.filter_by(form_type=form_type)
        if active_only:
            query = query.filter_by(is_active=True)

        query = query.order_by(Form.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def submit_response(form_id, user, responses, service_request_id=None):
        """Submit a response to a form"""
        form = Form.query.get(form_id)
        if not form:
            raise NotFoundError('Form not found')

        # Validate required questions
        for question in form.questions:
            if question.is_required:
                answer = responses.get(str(question.id))
                if answer is None or answer == '' or (isinstance(answer, list) and len(answer) == 0):
                    raise ValidationError(f'"{question.question_text}" is required')

        response = FormResponse(
            form_id=form_id,
            user_id=user.id,
            service_request_id=service_request_id,
            responses=responses
        )
        db.session.add(response)
        db.session.commit()

        return response

    @staticmethod
    def get_response(response_id):
        """Get a form response by ID"""
        response = FormResponse.query.get(response_id)
        if not response:
            raise NotFoundError('Response not found')
        return response

    @staticmethod
    def get_responses_for_form(form_id, page=1, per_page=20):
        """Get all responses for a form"""
        return FormResponse.query.filter_by(form_id=form_id).order_by(
            FormResponse.submitted_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_responses_for_request(service_request_id):
        """Get form responses for a specific service request"""
        return FormResponse.query.filter_by(service_request_id=service_request_id).all()
