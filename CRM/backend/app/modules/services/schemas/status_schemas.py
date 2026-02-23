"""
Schemas for request status validation.
"""

from marshmallow import Schema, fields, validate


class StatusSchema(Schema):
    """Schema for status response"""
    id = fields.Int(dump_only=True)
    status_key = fields.Str()
    display_name = fields.Str()
    description = fields.Str()
    color = fields.Str()
    position = fields.Int()
    wip_limit = fields.Int(allow_none=True)
    is_final = fields.Bool()
    is_active = fields.Bool()
    category = fields.Str()
    is_default = fields.Bool()
    is_system = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CreateStatusSchema(Schema):
    """Schema for creating a custom status"""
    status_key = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=50),
            validate.Regexp(r'^[a-z][a-z0-9_]*$', error='Status key must be lowercase with underscores only')
        ]
    )
    display_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    color = fields.Str(
        load_default='#6B7280',
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error='Color must be a valid hex color')
    )
    position = fields.Int(load_default=0)
    wip_limit = fields.Int(allow_none=True, validate=validate.Range(min=1))
    is_final = fields.Bool(load_default=False)
    category = fields.Str(
        load_default='request',
        validate=validate.OneOf(['request', 'task', 'both'])
    )
    is_default = fields.Bool(load_default=False)


class UpdateStatusSchema(Schema):
    """Schema for updating a custom status"""
    display_name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    color = fields.Str(
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error='Color must be a valid hex color')
    )
    position = fields.Int()
    wip_limit = fields.Int(allow_none=True, validate=validate.Range(min=1))
    is_final = fields.Bool()
    is_active = fields.Bool()
    category = fields.Str(validate=validate.OneOf(['request', 'task', 'both']))
    is_default = fields.Bool()


class ReorderStatusesSchema(Schema):
    """Schema for reordering statuses"""
    status_ids = fields.List(
        fields.Int(),
        required=True,
        validate=validate.Length(min=1)
    )


class InitializeCustomStatusesSchema(Schema):
    """Schema for initializing custom statuses from system defaults"""
    copy_from_system = fields.Bool(load_default=True)
