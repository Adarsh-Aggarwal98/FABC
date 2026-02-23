"""
Response Schemas - Validation schemas for form responses
"""
from marshmallow import Schema, fields


class SubmitResponseSchema(Schema):
    """Schema for submitting form responses"""
    responses = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),  # Can be string, list, number, etc.
        required=True
    )
    service_request_id = fields.Str()
    partial = fields.Bool(load_default=False)  # Staff can skip required field validation


class FormResponseSchema(Schema):
    """Schema for form response output"""
    id = fields.Int()
    form_id = fields.Int()
    user_id = fields.Str()
    service_request_id = fields.Str()
    responses = fields.Dict()
    submitted_at = fields.DateTime()
