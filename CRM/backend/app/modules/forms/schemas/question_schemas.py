"""
Question Schemas - Validation schemas for form questions
"""
from marshmallow import Schema, fields, validate, validates
from app.modules.forms.models.form_question import FormQuestion


class QuestionSchema(Schema):
    """Schema for form questions"""
    id = fields.Int(dump_only=True)
    question_text = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    question_type = fields.Str(
        required=True,
        validate=validate.OneOf(FormQuestion.VALID_TYPES)
    )
    is_required = fields.Bool(load_default=False)
    allow_attachment = fields.Bool(load_default=False)
    options = fields.List(fields.Str())  # For select, multiselect, radio, checkbox
    validation_rules = fields.Dict()
    placeholder = fields.Str(validate=validate.Length(max=200))
    help_text = fields.Str(validate=validate.Length(max=500))
    order = fields.Int()

    @validates('options')
    def validate_options(self, value, **kwargs):
        # Options required for certain question types
        pass


class AddQuestionSchema(Schema):
    """Schema for adding a question to a form"""
    question_text = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    question_type = fields.Str(
        required=True,
        validate=validate.OneOf(FormQuestion.VALID_TYPES)
    )
    is_required = fields.Bool(load_default=False)
    allow_attachment = fields.Bool(load_default=False)
    options = fields.List(fields.Str())
    validation_rules = fields.Dict()
    placeholder = fields.Str(validate=validate.Length(max=200))
    help_text = fields.Str(validate=validate.Length(max=500))
    order = fields.Int()


class UpdateQuestionSchema(Schema):
    """Schema for updating a question"""
    question_text = fields.Str(validate=validate.Length(min=1, max=500))
    question_type = fields.Str(validate=validate.OneOf(FormQuestion.VALID_TYPES))
    is_required = fields.Bool()
    allow_attachment = fields.Bool()
    options = fields.List(fields.Str())
    validation_rules = fields.Dict()
    placeholder = fields.Str(validate=validate.Length(max=200))
    help_text = fields.Str(validate=validate.Length(max=500))
    order = fields.Int()


class ReorderQuestionsSchema(Schema):
    """Schema for reordering questions"""
    question_orders = fields.List(
        fields.Dict(keys=fields.Str(), values=fields.Int()),
        required=True
    )
