"""
Service Catalog Schemas

Marshmallow schemas for service catalog validation.
"""
from marshmallow import Schema, fields, validate


class ServiceSchema(Schema):
    """Schema for service catalog"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    category = fields.Str(validate=validate.Length(max=100))
    base_price = fields.Decimal(as_string=True, places=2)
    is_active = fields.Bool()
    form_id = fields.Int(allow_none=True)
    workflow_id = fields.Str(allow_none=True)
    cost_percentage = fields.Decimal(as_string=True, places=2, allow_none=True)
    cost_category = fields.Str(validate=validate.Length(max=50), allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class CreateServiceSchema(Schema):
    """Schema for creating a service"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    category = fields.Str(validate=validate.Length(max=100))
    base_price = fields.Decimal(as_string=True, places=2)
    is_active = fields.Bool(load_default=True)
    form_id = fields.Int(allow_none=True)
    workflow_id = fields.Str(allow_none=True)
    cost_percentage = fields.Decimal(as_string=True, places=2, allow_none=True)
    cost_category = fields.Str(validate=validate.Length(max=50), allow_none=True)


class UpdateServiceSchema(Schema):
    """Schema for updating a service"""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    category = fields.Str(validate=validate.Length(max=100))
    base_price = fields.Decimal(as_string=True, places=2)
    is_active = fields.Bool()
    form_id = fields.Int(allow_none=True)
    workflow_id = fields.Str(allow_none=True)
    cost_percentage = fields.Decimal(as_string=True, places=2, allow_none=True)
    cost_category = fields.Str(validate=validate.Length(max=50), allow_none=True)
