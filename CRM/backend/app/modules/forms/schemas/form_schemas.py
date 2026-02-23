"""
Form Schemas - Validation schemas for forms
"""
from marshmallow import Schema, fields, validate, post_load
from app.modules.forms.schemas.question_schemas import QuestionSchema


class CreateFormSchema(Schema):
    """Schema for creating a form"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    form_type = fields.Str(
        required=True,
        validate=validate.OneOf(['service', 'onboarding', 'general'])
    )
    # Accept both 'questions' and 'fields' for backward compatibility
    questions = fields.List(fields.Nested(QuestionSchema), load_default=None)
    # Alias for questions
    fields_alias = fields.List(fields.Nested(QuestionSchema), data_key='fields', load_default=None)


    @post_load
    def process_fields(self, data, **kwargs):
        # If 'fields' was provided, use it as 'questions'
        if data.get('fields_alias') and not data.get('questions'):
            data['questions'] = data.pop('fields_alias')
        elif 'fields_alias' in data:
            del data['fields_alias']
        return data


class UpdateFormSchema(Schema):
    """Schema for updating a form"""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    is_active = fields.Bool()


class CloneFormSchema(Schema):
    """Schema for cloning a form"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()


class UpdateFormStatusSchema(Schema):
    """Schema for updating form status (publish/archive)"""
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['draft', 'published', 'archived'])
    )


class ListDefaultFormsSchema(Schema):
    """Schema for listing default forms"""
    include_questions = fields.Bool(load_default=False)
