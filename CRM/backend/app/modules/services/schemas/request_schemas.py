"""
Service Request Schemas

Marshmallow schemas for service request validation.
"""
from marshmallow import Schema, fields, validate


class CreateRequestSchema(Schema):
    """Schema for creating a service request"""
    service_id = fields.Int(required=True)
    user_id = fields.Str(allow_none=True)
    client_entity_id = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    internal_reference = fields.Str(validate=validate.Length(max=100), allow_none=True)
    xero_reference_job_id = fields.Str(validate=validate.Length(max=100), allow_none=True)


class CreateMultipleRequestsSchema(Schema):
    """Schema for creating multiple service requests"""
    service_ids = fields.List(fields.Int(), required=True)
    user_id = fields.Str(allow_none=True)
    client_entity_id = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    internal_reference = fields.Str(validate=validate.Length(max=100), allow_none=True)
    xero_reference_job_id = fields.Str(validate=validate.Length(max=100), allow_none=True)


class AssignRequestSchema(Schema):
    """Schema for assigning a request"""
    accountant_id = fields.Str(required=True)
    deadline_date = fields.Date(allow_none=True)
    priority = fields.Str(
        validate=validate.OneOf(['low', 'normal', 'high', 'urgent']),
        allow_none=True
    )


class UpdateStatusSchema(Schema):
    """Schema for updating request status"""
    status = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )


class UpdateInvoiceSchema(Schema):
    """Schema for updating invoice details on a request"""
    invoice_raised = fields.Bool()
    invoice_paid = fields.Bool()
    invoice_amount = fields.Decimal(as_string=True, places=2)
    payment_link = fields.Str(validate=validate.Length(max=500))


class UpdateCostSchema(Schema):
    """Schema for updating cost details on a service request"""
    actual_cost = fields.Decimal(as_string=True, places=2, allow_none=True)
    cost_notes = fields.Str(allow_none=True)
    labor_hours = fields.Decimal(as_string=True, places=2, allow_none=True)
    labor_rate = fields.Decimal(as_string=True, places=2, allow_none=True)


class AddNoteSchema(Schema):
    """Schema for adding internal note"""
    note = fields.Str(required=True, validate=validate.Length(min=1))


class ServiceRequestListSchema(Schema):
    """Schema for service request list"""
    id = fields.Str()
    service = fields.Dict()
    user = fields.Dict()
    status = fields.Str()
    invoice_raised = fields.Bool()
    invoice_paid = fields.Bool()
    created_at = fields.DateTime()
