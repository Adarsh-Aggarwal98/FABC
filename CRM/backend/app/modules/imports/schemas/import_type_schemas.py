"""
Import Type Schemas

Defines the metadata for available import types.
"""
from typing import List

from app.modules.imports.models import ImportType


def get_base_import_types() -> List[ImportType]:
    """Get the base import types available to all admin users."""
    return [
        ImportType(
            id='clients',
            name='Clients',
            description='Import client/user data with contact information',
            required_columns=['email', 'first_name', 'last_name'],
            optional_columns=[
                'phone', 'address', 'date_of_birth', 'occupation',
                'company_name', 'abn', 'tfn', 'personal_email',
                'bsb', 'bank_account_number', 'bank_account_holder_name'
            ]
        ),
        ImportType(
            id='service_requests',
            name='Service Requests',
            description='Import existing jobs/requests with their status and details',
            required_columns=['client_email', 'service_name'],
            optional_columns=[
                'status', 'description', 'priority', 'deadline_date',
                'invoice_amount', 'invoice_raised', 'invoice_paid',
                'internal_reference', 'internal_notes', 'created_date'
            ]
        ),
        ImportType(
            id='services',
            name='Services Catalog',
            description='Import or update service offerings with pricing',
            required_columns=['name'],
            optional_columns=[
                'description', 'category', 'base_price', 'is_recurring',
                'renewal_period_months', 'cost_percentage'
            ]
        )
    ]


def get_super_admin_import_types() -> List[ImportType]:
    """Get additional import types available only to super admins."""
    return [
        ImportType(
            id='companies',
            name='Companies',
            description='Import new companies/practices with admin users',
            required_columns=['name', 'admin_email'],
            optional_columns=[
                'trading_name', 'abn', 'acn', 'email', 'phone',
                'address', 'website', 'tax_agent_number',
                'admin_first_name', 'admin_last_name'
            ]
        )
    ]


def get_all_import_types(is_super_admin: bool = False) -> List[ImportType]:
    """
    Get all import types available to a user based on their role.

    Args:
        is_super_admin: Whether the user is a super admin

    Returns:
        List of ImportType objects
    """
    types = get_base_import_types()
    if is_super_admin:
        types.extend(get_super_admin_import_types())
    return types


# Valid statuses for service requests
VALID_SERVICE_REQUEST_STATUSES = [
    'pending', 'invoice_raised', 'assigned', 'query_raised',
    'accountant_review_pending', 'processing', 'completed'
]

# Valid priorities for service requests
VALID_PRIORITIES = ['low', 'normal', 'high', 'urgent']
