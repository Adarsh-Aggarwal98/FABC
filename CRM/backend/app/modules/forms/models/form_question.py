"""
FormQuestion Model - Individual question in a form
"""
from datetime import datetime
from app.extensions import db


class FormQuestion(db.Model):
    """Individual question in a form"""
    __tablename__ = 'form_questions'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # text, textarea, select, multiselect, radio, checkbox, date, file, number
    is_required = db.Column(db.Boolean, default=False)
    allow_attachment = db.Column(db.Boolean, default=False)  # Allow user to attach files to this question
    options = db.Column(db.JSON)  # For select, multiselect, radio, checkbox - stores list of options
    validation_rules = db.Column(db.JSON)  # min, max, pattern, etc.
    placeholder = db.Column(db.String(200))
    help_text = db.Column(db.String(500))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Section support for multi-section forms
    section_number = db.Column(db.Integer, default=1)  # Which section this question belongs to
    section_title = db.Column(db.String(200))  # Title of the section (only needed for first question in section)
    section_description = db.Column(db.Text)  # Optional description for the section

    # Repeatable sections - allows user to add multiple instances (e.g., multiple directors)
    is_section_repeatable = db.Column(db.Boolean, default=False)  # Can this section be repeated?
    section_group = db.Column(db.String(50))  # Group name for repeatable sections (e.g., 'director', 'shareholder')
    min_section_repeats = db.Column(db.Integer, default=1)  # Minimum number of repeats required
    max_section_repeats = db.Column(db.Integer, default=10)  # Maximum number of repeats allowed

    # Conditional logic - show this question based on another question's answer
    conditional_on_question_id = db.Column(db.Integer, db.ForeignKey('form_questions.id'), nullable=True)
    conditional_value = db.Column(db.String(200))  # Show if the referenced question has this value

    # Question types
    TYPE_TEXT = 'text'
    TYPE_TEXTAREA = 'textarea'
    TYPE_NUMBER = 'number'
    TYPE_EMAIL = 'email'
    TYPE_PHONE = 'phone'
    TYPE_DATE = 'date'
    TYPE_SELECT = 'select'
    TYPE_MULTISELECT = 'multiselect'
    TYPE_RADIO = 'radio'
    TYPE_CHECKBOX = 'checkbox'
    TYPE_FILE = 'file'

    VALID_TYPES = [
        TYPE_TEXT, TYPE_TEXTAREA, TYPE_NUMBER, TYPE_EMAIL, TYPE_PHONE,
        TYPE_DATE, TYPE_SELECT, TYPE_MULTISELECT, TYPE_RADIO, TYPE_CHECKBOX, TYPE_FILE
    ]

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'is_required': self.is_required,
            'allow_attachment': self.allow_attachment,
            'options': self.options,
            'validation_rules': self.validation_rules,
            'placeholder': self.placeholder,
            'help_text': self.help_text,
            'order': self.order,
            'section_number': self.section_number,
            'section_title': self.section_title,
            'section_description': self.section_description,
            'is_section_repeatable': self.is_section_repeatable,
            'section_group': self.section_group,
            'min_section_repeats': self.min_section_repeats,
            'max_section_repeats': self.max_section_repeats,
            'conditional_on_question_id': self.conditional_on_question_id,
            'conditional_value': self.conditional_value
        }

    def __repr__(self):
        return f'<FormQuestion {self.question_text[:30]}>'
