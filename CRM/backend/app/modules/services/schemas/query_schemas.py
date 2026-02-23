"""
Query Schemas

Marshmallow schemas for query/message validation.
"""
from marshmallow import Schema, fields, validate


class CreateQuerySchema(Schema):
    """Schema for creating a query"""
    message = fields.Str(required=True, validate=validate.Length(min=1))
    attachment_url = fields.Str(validate=validate.Length(max=500))


class QuerySchema(Schema):
    """Schema for query response"""
    id = fields.Int()
    message = fields.Str()
    attachment_url = fields.Str()
    sender = fields.Dict()
    created_at = fields.DateTime()
