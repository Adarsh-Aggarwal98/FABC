"""
Email Automation Schemas - Validation schemas for email automation operations
"""
from marshmallow import Schema, fields, validate

from app.modules.notifications.models.email_automation import EmailAutomation


class EmailAutomationSchema(Schema):
    """Schema for creating an email automation"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()

    trigger_type = fields.Str(
        required=True,
        validate=validate.OneOf(EmailAutomation.VALID_TRIGGERS)
    )
    trigger_config = fields.Dict()  # Additional trigger parameters

    template_id = fields.Int()  # Template to use
    custom_subject = fields.Str(validate=validate.Length(max=500))
    custom_body = fields.Str()
    delay_minutes = fields.Int(load_default=0)

    conditions = fields.Dict()  # Additional conditions
    is_active = fields.Bool(load_default=True)


class UpdateEmailAutomationSchema(Schema):
    """Schema for updating an email automation"""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    trigger_config = fields.Dict()
    template_id = fields.Int()
    custom_subject = fields.Str(validate=validate.Length(max=500))
    custom_body = fields.Str()
    delay_minutes = fields.Int()
    conditions = fields.Dict()
    is_active = fields.Bool()
