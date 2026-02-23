"""
ClientEntityContact Schemas
============================
Marshmallow schemas for ClientEntityContact validation and serialization.
"""

from marshmallow import Schema, fields, validate
from ..models import ClientEntityContact


class ClientEntityContactSchema(Schema):
    """Schema for ClientEntityContact."""
    id = fields.Int(dump_only=True)
    client_entity_id = fields.Str(dump_only=True)
    user_id = fields.Str(allow_none=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    position = fields.Str(validate=validate.Length(max=100), allow_none=True)
    contact_type = fields.Str(
        validate=validate.OneOf(ClientEntityContact.VALID_TYPES),
        load_default=ClientEntityContact.TYPE_PRIMARY
    )
    is_primary = fields.Bool(load_default=False)
    effective_from = fields.Date(allow_none=True)
    effective_to = fields.Date(allow_none=True)
    is_active = fields.Bool(load_default=True)
    notes = fields.Str(allow_none=True)


class CreateClientEntityContactSchema(Schema):
    """Schema for creating a ClientEntityContact."""
    user_id = fields.Str(allow_none=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    position = fields.Str(validate=validate.Length(max=100), allow_none=True)
    contact_type = fields.Str(
        validate=validate.OneOf(ClientEntityContact.VALID_TYPES),
        load_default=ClientEntityContact.TYPE_PRIMARY
    )
    is_primary = fields.Bool(load_default=False)
    effective_from = fields.Date(allow_none=True)
    notes = fields.Str(allow_none=True)


class UpdateClientEntityContactSchema(Schema):
    """Schema for updating a ClientEntityContact."""
    user_id = fields.Str(allow_none=True)  # Link/unlink to a user account
    first_name = fields.Str(validate=validate.Length(min=1, max=100))
    last_name = fields.Str(validate=validate.Length(min=1, max=100))
    email = fields.Email(allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    position = fields.Str(validate=validate.Length(max=100), allow_none=True)
    contact_type = fields.Str(validate=validate.OneOf(ClientEntityContact.VALID_TYPES))
    is_primary = fields.Bool()
    effective_to = fields.Date(allow_none=True)
    is_active = fields.Bool()
    notes = fields.Str(allow_none=True)
