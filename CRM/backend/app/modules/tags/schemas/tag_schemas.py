"""
Tags module validation schemas.
"""
from marshmallow import Schema, fields, validate


class CreateTagSchema(Schema):
    """Schema for creating a new tag"""
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    color = fields.String(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error='Invalid hex color format'))


class UpdateTagSchema(Schema):
    """Schema for updating an existing tag"""
    name = fields.String(validate=validate.Length(min=1, max=50))
    color = fields.String(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error='Invalid hex color format'))


class AssignTagSchema(Schema):
    """Schema for assigning a tag to a user"""
    tag_id = fields.Integer(required=True)
