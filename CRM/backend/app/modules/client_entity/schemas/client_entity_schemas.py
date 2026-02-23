"""
ClientEntity Schemas
=====================
Marshmallow schemas for ClientEntity validation and serialization.
"""

from marshmallow import Schema, fields, validate, validates
from ..models import ClientEntity
from .client_entity_contact_schemas import (
    ClientEntityContactSchema,
    CreateClientEntityContactSchema
)


class TrustDetailsSchema(Schema):
    """Schema for trust-specific details."""
    trust_type = fields.Str(
        validate=validate.OneOf(ClientEntity.VALID_TRUST_TYPES),
        allow_none=True
    )
    trustee_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    trust_deed_date = fields.Date(allow_none=True)


class AddressSchema(Schema):
    """Schema for address fields."""
    line1 = fields.Str(validate=validate.Length(max=200), allow_none=True)
    line2 = fields.Str(validate=validate.Length(max=200), allow_none=True)
    city = fields.Str(validate=validate.Length(max=100), allow_none=True)
    state = fields.Str(validate=validate.Length(max=50), allow_none=True)
    postcode = fields.Str(validate=validate.Length(max=10), allow_none=True)
    country = fields.Str(validate=validate.Length(max=100), load_default='Australia')


class ClientEntitySchema(Schema):
    """Schema for ClientEntity."""
    id = fields.Str(dump_only=True)
    company_id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    trading_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    entity_type = fields.Str(
        required=True,
        validate=validate.OneOf(ClientEntity.VALID_TYPES)
    )
    abn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    acn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    tfn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    trust_details = fields.Nested(TrustDetailsSchema, allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    address = fields.Nested(AddressSchema, allow_none=True)
    financial_year_end_month = fields.Int(validate=validate.Range(min=1, max=12), load_default=6)
    financial_year_end_day = fields.Int(validate=validate.Range(min=1, max=31), load_default=30)
    xero_contact_id = fields.Str(validate=validate.Length(max=100), allow_none=True)
    is_active = fields.Bool(load_default=True)
    notes = fields.Str(allow_none=True)
    primary_contact = fields.Nested(ClientEntityContactSchema, dump_only=True)
    contacts = fields.List(fields.Nested(ClientEntityContactSchema), dump_only=True)


class CreateClientEntitySchema(Schema):
    """Schema for creating a ClientEntity."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    trading_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    entity_type = fields.Str(
        required=True,
        validate=validate.OneOf(ClientEntity.VALID_TYPES)
    )
    abn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    acn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    tfn = fields.Str(validate=validate.Length(max=20), allow_none=True)

    # Trust-specific fields (can be nested or flat)
    trust_type = fields.Str(
        validate=validate.OneOf(ClientEntity.VALID_TRUST_TYPES),
        allow_none=True
    )
    trustee_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    trust_deed_date = fields.Date(allow_none=True)

    email = fields.Email(allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

    # Address fields (flat)
    address_line1 = fields.Str(validate=validate.Length(max=200), allow_none=True)
    address_line2 = fields.Str(validate=validate.Length(max=200), allow_none=True)
    city = fields.Str(validate=validate.Length(max=100), allow_none=True)
    state = fields.Str(validate=validate.Length(max=50), allow_none=True)
    postcode = fields.Str(validate=validate.Length(max=10), allow_none=True)
    country = fields.Str(validate=validate.Length(max=100), load_default='Australia')

    financial_year_end_month = fields.Int(validate=validate.Range(min=1, max=12), load_default=6)
    financial_year_end_day = fields.Int(validate=validate.Range(min=1, max=31), load_default=30)
    xero_contact_id = fields.Str(validate=validate.Length(max=100), allow_none=True)
    notes = fields.Str(allow_none=True)

    # Optional: Create initial contact
    primary_contact = fields.Nested(CreateClientEntityContactSchema, allow_none=True)

    @validates('entity_type')
    def validate_trust_fields(self, value):
        """Validate trust-specific fields are present for trusts."""
        # This is optional - trusts can be created without trust details initially
        pass


class UpdateClientEntitySchema(Schema):
    """Schema for updating a ClientEntity."""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    trading_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    entity_type = fields.Str(validate=validate.OneOf(ClientEntity.VALID_TYPES))
    abn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    acn = fields.Str(validate=validate.Length(max=20), allow_none=True)
    tfn = fields.Str(validate=validate.Length(max=20), allow_none=True)

    # Trust-specific fields
    trust_type = fields.Str(
        validate=validate.OneOf(ClientEntity.VALID_TRUST_TYPES),
        allow_none=True
    )
    trustee_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
    trust_deed_date = fields.Date(allow_none=True)

    email = fields.Email(allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

    # Address fields
    address_line1 = fields.Str(validate=validate.Length(max=200), allow_none=True)
    address_line2 = fields.Str(validate=validate.Length(max=200), allow_none=True)
    city = fields.Str(validate=validate.Length(max=100), allow_none=True)
    state = fields.Str(validate=validate.Length(max=50), allow_none=True)
    postcode = fields.Str(validate=validate.Length(max=10), allow_none=True)
    country = fields.Str(validate=validate.Length(max=100), allow_none=True)

    financial_year_end_month = fields.Int(validate=validate.Range(min=1, max=12))
    financial_year_end_day = fields.Int(validate=validate.Range(min=1, max=31))
    xero_contact_id = fields.Str(validate=validate.Length(max=100), allow_none=True)
    is_active = fields.Bool()
    notes = fields.Str(allow_none=True)


class ClientEntitySearchSchema(Schema):
    """Schema for search parameters."""
    q = fields.Str(validate=validate.Length(min=1))
    entity_type = fields.Str(validate=validate.OneOf(ClientEntity.VALID_TYPES))
    is_active = fields.Bool()
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


class ClientEntityListSchema(Schema):
    """Schema for list parameters."""
    entity_type = fields.Str(validate=validate.OneOf(ClientEntity.VALID_TYPES))
    is_active = fields.Bool()
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=500))
    sort_by = fields.Str(
        validate=validate.OneOf(['name', 'created_at', 'updated_at', 'entity_type']),
        load_default='name'
    )
    sort_order = fields.Str(
        validate=validate.OneOf(['asc', 'desc']),
        load_default='asc'
    )
