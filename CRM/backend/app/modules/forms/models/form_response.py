"""
FormResponse Model - User's response to a form
"""
from datetime import datetime
from app.extensions import db


class FormResponse(db.Model):
    """User's response to a form - stores complete snapshot for data integrity"""
    __tablename__ = 'form_responses'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id'), nullable=True)

    # Store complete snapshot with questions and answers for data integrity
    # Format: { "form_snapshot": {...}, "responses": [...], "metadata": {...} }
    response_data = db.Column(db.JSON, nullable=False)

    # Legacy field for backward compatibility - deprecated
    responses = db.Column(db.JSON)  # {question_id: answer}

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Status for draft/submitted forms
    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    status = db.Column(db.String(20), default=STATUS_SUBMITTED)

    # Relationships
    form = db.relationship('Form', backref='responses')
    user = db.relationship('User', backref='form_responses')

    @classmethod
    def create_with_snapshot(cls, form, user_id, answers, service_request_id=None):
        """
        Create a form response with complete snapshot.

        Args:
            form: Form model instance
            user_id: ID of the user submitting
            answers: List of {question_id, answer, attachments} or dict {question_id: answer}
            service_request_id: Optional service request ID

        Returns:
            FormResponse instance with complete snapshot
        """
        # Build form snapshot
        form_snapshot = {
            'id': form.id,
            'name': form.name,
            'description': form.description,
            'form_type': form.form_type,
            'captured_at': datetime.utcnow().isoformat()
        }

        # Build responses with question context
        response_items = []
        questions_dict = {q.id: q for q in form.questions}

        # Handle both dict and list formats
        if isinstance(answers, dict):
            for q_id, answer in answers.items():
                question = questions_dict.get(int(q_id))
                if question:
                    response_items.append({
                        'question_id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type,
                        'section_number': question.section_number,
                        'section_title': question.section_title,
                        'answer': answer,
                        'attachments': []
                    })
        else:
            for item in answers:
                q_id = item.get('question_id')
                question = questions_dict.get(int(q_id)) if q_id else None
                if question:
                    response_items.append({
                        'question_id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type,
                        'section_number': question.section_number,
                        'section_title': question.section_title,
                        'answer': item.get('answer'),
                        'attachments': item.get('attachments', [])
                    })

        response_data = {
            'form_snapshot': form_snapshot,
            'responses': response_items,
            'metadata': {
                'submitted_by': user_id,
                'submitted_at': datetime.utcnow().isoformat(),
                'version': '2.0'  # Version for future schema changes
            }
        }

        return cls(
            form_id=form.id,
            user_id=user_id,
            service_request_id=service_request_id,
            response_data=response_data,
            responses={str(item['question_id']): item['answer'] for item in response_items}  # Legacy support
        )

    def to_dict(self, include_questions=False, include_snapshot=False):
        data = {
            'id': self.id,
            'form_id': self.form_id,
            'user_id': self.user_id,
            'service_request_id': self.service_request_id,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Use response_data if available (new format), fallback to responses (legacy)
        if self.response_data:
            data['responses'] = self.response_data.get('responses', [])
            if include_snapshot:
                data['form_snapshot'] = self.response_data.get('form_snapshot')
                data['metadata'] = self.response_data.get('metadata')
            # Also provide detailed_responses in consistent format for UI
            if include_questions:
                detailed_responses = []
                for item in self.response_data.get('responses', []):
                    detailed_responses.append({
                        'question': item.get('question_text', ''),
                        'question_type': item.get('question_type', 'text'),
                        'answer': item.get('answer'),
                        'section_title': item.get('section_title')
                    })
                data['detailed_responses'] = detailed_responses
        else:
            data['responses'] = self.responses
            if include_questions:
                # Legacy: Include question text with responses from current form
                detailed_responses = []
                for question in self.form.questions:
                    answer = self.responses.get(str(question.id)) if self.responses else None
                    detailed_responses.append({
                        'question': question.question_text,
                        'question_type': question.question_type,
                        'answer': answer
                    })
                data['detailed_responses'] = detailed_responses

        return data

    def __repr__(self):
        return f'<FormResponse {self.id} for form {self.form_id}>'
