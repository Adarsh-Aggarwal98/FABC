"""
Scheduled Email Schemas - Validation schemas for scheduled email operations
"""
from marshmallow import Schema, fields, validate


class ScheduledEmailSchema(Schema):
    """Schema for creating a scheduled email"""
    recipient_type = fields.Str(
        required=True,
        validate=validate.OneOf(['single', 'group', 'filter'])
    )
    recipient_email = fields.Email()  # For single recipient (external)
    recipient_user_id = fields.Str()  # For single recipient (user)
    recipient_filter = fields.Dict()  # For filtered recipients

    subject = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    body_html = fields.Str()  # Custom body (if not using template)
    template_id = fields.Int()  # Template to use
    template_context = fields.Dict()  # Variables for template

    scheduled_at = fields.DateTime(required=True)
    timezone = fields.Str(validate=validate.Length(max=50), load_default='UTC')


class UpdateScheduledEmailSchema(Schema):
    """Schema for updating a scheduled email"""
    subject = fields.Str(validate=validate.Length(min=1, max=500))
    body_html = fields.Str()
    template_id = fields.Int()
    template_context = fields.Dict()
    scheduled_at = fields.DateTime()
    timezone = fields.Str(validate=validate.Length(max=50))
