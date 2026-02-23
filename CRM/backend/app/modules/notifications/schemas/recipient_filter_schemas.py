"""
Recipient Filter Schemas - Validation schemas for recipient filtering
"""
from marshmallow import Schema, fields


class RecipientFilterSchema(Schema):
    """Schema for recipient filter criteria"""
    roles = fields.List(fields.Str())  # Filter by role: client, accountant
    tags = fields.List(fields.Str())  # Filter by user tags
    status = fields.Str()  # Filter by user status
    service_ids = fields.List(fields.Int())  # Users who have requested these services
    created_after = fields.Date()  # Users created after this date
    created_before = fields.Date()  # Users created before this date
    has_outstanding_invoices = fields.Bool()  # Users with unpaid invoices
