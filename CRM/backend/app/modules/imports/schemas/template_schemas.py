"""
Template Schemas

Defines the template configurations for each import type.
"""
from typing import Tuple, List, Dict, Any

from app.modules.imports.models import ImportTemplate


def get_clients_template() -> ImportTemplate:
    """Template for client/user import."""
    columns = [
        'email', 'first_name', 'last_name', 'phone', 'address',
        'date_of_birth', 'occupation', 'company_name', 'abn', 'tfn',
        'personal_email', 'bsb', 'bank_account_number', 'bank_account_holder_name'
    ]
    sample_rows = [
        {
            'email': 'john.smith@example.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'phone': '0412345678',
            'address': '123 Main Street, Sydney NSW 2000',
            'date_of_birth': '1985-06-15',
            'occupation': 'Software Engineer',
            'company_name': 'Smith Tech Pty Ltd',
            'abn': '12345678901',
            'tfn': '',
            'personal_email': 'john.personal@gmail.com',
            'bsb': '062-000',
            'bank_account_number': '12345678',
            'bank_account_holder_name': 'John Smith'
        },
        {
            'email': 'jane.doe@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '0498765432',
            'address': '456 Oak Avenue, Melbourne VIC 3000',
            'date_of_birth': '1990-03-22',
            'occupation': 'Marketing Manager',
            'company_name': '',
            'abn': '',
            'tfn': '',
            'personal_email': '',
            'bsb': '',
            'bank_account_number': '',
            'bank_account_holder_name': ''
        }
    ]
    return ImportTemplate(
        data_type='clients',
        columns=columns,
        sample_rows=sample_rows,
        filename='client_import_template.csv'
    )


def get_service_requests_template() -> ImportTemplate:
    """Template for service request import."""
    columns = [
        'client_email', 'service_name', 'status', 'description',
        'priority', 'deadline_date', 'invoice_amount', 'invoice_raised',
        'invoice_paid', 'internal_reference', 'internal_notes', 'created_date'
    ]
    sample_rows = [
        {
            'client_email': 'john.smith@example.com',
            'service_name': 'Individual Tax Return',
            'status': 'pending',
            'description': 'FY2024 tax return preparation',
            'priority': 'normal',
            'deadline_date': '2024-10-31',
            'invoice_amount': '550.00',
            'invoice_raised': 'no',
            'invoice_paid': 'no',
            'internal_reference': 'TAX-2024-001',
            'internal_notes': 'Client has multiple income sources',
            'created_date': '2024-07-15'
        },
        {
            'client_email': 'jane.doe@example.com',
            'service_name': 'Business Activity Statement (BAS)',
            'status': 'processing',
            'description': 'Q2 BAS preparation',
            'priority': 'high',
            'deadline_date': '2024-08-28',
            'invoice_amount': '330.00',
            'invoice_raised': 'yes',
            'invoice_paid': 'no',
            'internal_reference': 'BAS-2024-Q2-002',
            'internal_notes': '',
            'created_date': '2024-08-01'
        },
        {
            'client_email': 'john.smith@example.com',
            'service_name': 'Bookkeeping',
            'status': 'completed',
            'description': 'Monthly bookkeeping June 2024',
            'priority': 'low',
            'deadline_date': '',
            'invoice_amount': '275.00',
            'invoice_raised': 'yes',
            'invoice_paid': 'yes',
            'internal_reference': 'BK-2024-06-001',
            'internal_notes': 'Recurring monthly service',
            'created_date': '2024-06-01'
        }
    ]
    return ImportTemplate(
        data_type='service_requests',
        columns=columns,
        sample_rows=sample_rows,
        filename='service_requests_import_template.csv'
    )


def get_services_template() -> ImportTemplate:
    """Template for services/catalog import."""
    columns = [
        'name', 'description', 'category', 'base_price',
        'is_recurring', 'renewal_period_months', 'cost_percentage'
    ]
    sample_rows = [
        {
            'name': 'Annual Compliance Review',
            'description': 'Comprehensive annual compliance review for businesses',
            'category': 'Compliance',
            'base_price': '1500.00',
            'is_recurring': 'yes',
            'renewal_period_months': '12',
            'cost_percentage': '35'
        },
        {
            'name': 'Business Advisory Session',
            'description': 'One-hour business advisory consultation',
            'category': 'Advisory',
            'base_price': '350.00',
            'is_recurring': 'no',
            'renewal_period_months': '',
            'cost_percentage': '25'
        }
    ]
    return ImportTemplate(
        data_type='services',
        columns=columns,
        sample_rows=sample_rows,
        filename='services_import_template.csv'
    )


def get_companies_template() -> ImportTemplate:
    """Template for company import (super admin only)."""
    columns = [
        'name', 'trading_name', 'abn', 'acn', 'email', 'phone',
        'address', 'website', 'tax_agent_number', 'admin_email',
        'admin_first_name', 'admin_last_name'
    ]
    sample_rows = [
        {
            'name': 'ABC Accounting Pty Ltd',
            'trading_name': 'ABC Accounting',
            'abn': '12345678901',
            'acn': '123456789',
            'email': 'info@abcaccounting.com.au',
            'phone': '02 9123 4567',
            'address': '100 George Street, Sydney NSW 2000',
            'website': 'https://www.abcaccounting.com.au',
            'tax_agent_number': '12345678',
            'admin_email': 'admin@abcaccounting.com.au',
            'admin_first_name': 'Michael',
            'admin_last_name': 'Johnson'
        }
    ]
    return ImportTemplate(
        data_type='companies',
        columns=columns,
        sample_rows=sample_rows,
        filename='companies_import_template.csv'
    )


# Template registry for easy lookup
TEMPLATES = {
    'clients': get_clients_template,
    'service_requests': get_service_requests_template,
    'services': get_services_template,
    'companies': get_companies_template,
}


def get_template(data_type: str) -> ImportTemplate:
    """
    Get the template for a specific data type.

    Args:
        data_type: The type of data template to get

    Returns:
        ImportTemplate for the specified type

    Raises:
        ValueError: If the data type is not recognized
    """
    if data_type not in TEMPLATES:
        raise ValueError(f'Unknown data type: {data_type}. Valid types: {", ".join(TEMPLATES.keys())}')
    return TEMPLATES[data_type]()


def get_available_template_types() -> List[str]:
    """Get list of available template types."""
    return list(TEMPLATES.keys())
