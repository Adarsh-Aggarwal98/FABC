"""
Invoice Schemas

Marshmallow schemas for invoice validation.
"""
from marshmallow import Schema, fields, validate


class InvoiceLineItemSchema(Schema):
    """Schema for invoice line items"""
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    quantity = fields.Decimal(as_string=True, places=2, load_default=1)
    unit_price = fields.Decimal(as_string=True, places=2, required=True)
    total = fields.Decimal(as_string=True, places=2, dump_only=True)
    service_id = fields.Int(allow_none=True)
    is_tax_exempt = fields.Bool(load_default=False)
    order = fields.Int(load_default=0)


class CreateInvoiceLineItemSchema(Schema):
    """Schema for creating invoice line items"""
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    quantity = fields.Decimal(as_string=True, places=2, load_default=1)
    unit_price = fields.Decimal(as_string=True, places=2, required=True)
    service_id = fields.Int(allow_none=True)
    is_tax_exempt = fields.Bool(load_default=False)


class CreateInvoiceSchema(Schema):
    """Schema for creating an invoice"""
    client_id = fields.Str(required=True)
    service_request_id = fields.Str(allow_none=True)
    reference = fields.Str(validate=validate.Length(max=100))
    due_date = fields.Date(required=True)
    tax_rate = fields.Decimal(as_string=True, places=2, load_default=10)
    discount_amount = fields.Decimal(as_string=True, places=2, load_default=0)
    discount_description = fields.Str(validate=validate.Length(max=200))
    notes = fields.Str()
    payment_terms = fields.Str()
    line_items = fields.List(fields.Nested(CreateInvoiceLineItemSchema), required=True)


class UpdateInvoiceDetailsSchema(Schema):
    """Schema for updating invoice details"""
    reference = fields.Str(validate=validate.Length(max=100))
    due_date = fields.Date()
    tax_rate = fields.Decimal(as_string=True, places=2)
    discount_amount = fields.Decimal(as_string=True, places=2)
    discount_description = fields.Str(validate=validate.Length(max=200))
    notes = fields.Str()
    internal_notes = fields.Str()
    payment_terms = fields.Str()


class AddInvoicePaymentSchema(Schema):
    """Schema for adding a payment to an invoice"""
    amount = fields.Decimal(as_string=True, places=2, required=True)
    payment_method = fields.Str(
        validate=validate.OneOf(['card', 'bank_transfer', 'cash', 'cheque', 'other']),
        load_default='card'
    )
    reference = fields.Str(validate=validate.Length(max=100))
    notes = fields.Str()
    payment_date = fields.Date()  # Accept date format YYYY-MM-DD


class SendInvoiceSchema(Schema):
    """Schema for sending an invoice"""
    send_email = fields.Bool(load_default=True)
    email_message = fields.Str()


class InvoiceSchema(Schema):
    """Schema for invoice response"""
    id = fields.Str()
    invoice_number = fields.Str()
    reference = fields.Str()
    company_id = fields.Str()
    client = fields.Dict()
    service_request_id = fields.Str()
    issue_date = fields.Date()
    due_date = fields.Date()
    subtotal = fields.Decimal(as_string=True)
    tax_rate = fields.Decimal(as_string=True)
    tax_amount = fields.Decimal(as_string=True)
    discount_amount = fields.Decimal(as_string=True)
    total = fields.Decimal(as_string=True)
    amount_paid = fields.Decimal(as_string=True)
    balance_due = fields.Decimal(as_string=True)
    currency = fields.Str()
    status = fields.Str()
    line_items = fields.List(fields.Nested(InvoiceLineItemSchema))
    created_at = fields.DateTime()


class InvoiceListSchema(Schema):
    """Schema for invoice list response"""
    id = fields.Str()
    invoice_number = fields.Str()
    client = fields.Dict()
    total = fields.Decimal(as_string=True)
    balance_due = fields.Decimal(as_string=True)
    status = fields.Str()
    due_date = fields.Date()
    created_at = fields.DateTime()
