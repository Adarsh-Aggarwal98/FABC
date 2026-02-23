"""
Company Service Settings Schemas

Marshmallow schemas for company-specific service settings validation.
"""
from marshmallow import Schema, fields, validate


class CompanyServiceSettingsSchema(Schema):
    """Schema for company service settings"""
    id = fields.Int(dump_only=True)
    company_id = fields.Int(dump_only=True)
    service_id = fields.Int(dump_only=True)
    is_active = fields.Bool()
    custom_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    custom_description = fields.Str(allow_none=True)
    custom_price = fields.Decimal(as_string=True, places=2, allow_none=True)
    display_order = fields.Int()
    is_featured = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UpdateCompanyServiceSettingsSchema(Schema):
    """Schema for updating company service settings"""
    is_active = fields.Bool()
    custom_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    custom_description = fields.Str(allow_none=True)
    custom_price = fields.Decimal(as_string=True, places=2, allow_none=True)
    display_order = fields.Int()
    is_featured = fields.Bool()


class ActivateServiceSchema(Schema):
    """Schema for activating/deactivating a service for a company"""
    is_active = fields.Bool(required=True)


class BulkServiceActivationSchema(Schema):
    """Schema for bulk activating/deactivating services"""
    service_ids = fields.List(fields.Int(), required=True)
    is_active = fields.Bool(required=True)
