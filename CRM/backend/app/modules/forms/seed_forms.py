"""
Seed data for service-specific forms.
Contains comprehensive form definitions for various services.

This module provides an idempotent seeding system:
- Forms are matched by name. If a form exists, its questions are updated in place.
- Service-to-form links are defined in FORM_SERVICE_REGISTRY and synced automatically.
- Running seed multiple times is safe and will converge to the correct state.
"""
from app.extensions import db
from app.modules.forms.models import Form, FormQuestion  # Works with both old and new structure


# =============================================================================
# FORM ↔ SERVICE REGISTRY
# =============================================================================
# Maps comprehensive form names to the service names they should be linked to.
# This is the single source of truth for form-service relationships.
# When adding a new form, add an entry here so it auto-links to its service.
# =============================================================================
FORM_SERVICE_REGISTRY = {
    # Comprehensive form name → Service name (must match DB exactly)
    'Company Incorporation Form': 'Company Incorporation',
    'SMSF Setup Form': 'SMSF Establishment',
    'Individual Tax Return Form': 'Individual Tax Return',
    'SMSF Annual Compliance Questionnaire': 'SMSF Tax Return',
    'SMSF Annual Audit Form': 'SMSF Annual Audit',
    'Company Annual Compliance Questionnaire': 'Company Tax Return',
    'SMSF Audit Procedure Checklist': 'SMSF Annual Audit',
}


def upsert_form_from_definition(form_def, creator_id=None):
    """
    Create or update a form from a definition dictionary (idempotent).

    If a form with the same name exists:
      - Deletes all existing questions (only if no responses reference them)
      - Re-creates questions from the definition
      - Updates form metadata
    If no form exists:
      - Creates the form and all questions

    Args:
        form_def: Form definition dictionary with 'name', 'sections', etc.
        creator_id: Optional user ID of the creator

    Returns:
        (Form instance, created: bool)
    """
    from app.modules.forms.models import FormResponse

    form_name = form_def['name']
    existing = Form.query.filter_by(name=form_name, company_id=None).first()
    created = False

    if existing:
        # Check if any responses exist for this form
        response_count = FormResponse.query.filter_by(form_id=existing.id).count()
        if response_count > 0:
            # Form has responses - don't delete questions, just update metadata
            existing.description = form_def.get('description', existing.description)
            existing.form_type = form_def.get('form_type', existing.form_type)
            existing.is_default = True
            db.session.commit()
            print(f'  [SKIP-QUESTIONS] "{form_name}" has {response_count} responses, updated metadata only')
            return existing, False

        # No responses - safe to rebuild questions
        FormQuestion.query.filter_by(form_id=existing.id).delete()
        existing.description = form_def.get('description', existing.description)
        existing.form_type = form_def.get('form_type', existing.form_type)
        existing.is_default = True
        db.session.flush()
        form = existing
        print(f'  [UPDATE] "{form_name}" - rebuilding {_count_questions(form_def)} questions')
    else:
        form = Form(
            name=form_name,
            description=form_def.get('description'),
            form_type=form_def.get('form_type', 'service'),
            created_by_id=creator_id,
            is_default=True
        )
        db.session.add(form)
        db.session.flush()
        created = True
        print(f'  [CREATE] "{form_name}" with {_count_questions(form_def)} questions')

    # Create questions from sections
    _create_questions_from_sections(form, form_def)
    db.session.commit()
    return form, created


def _count_questions(form_def):
    """Count total questions in a form definition."""
    count = 0
    for section in form_def.get('sections', []):
        questions = section.get('questions', [])
        count += len(questions) if questions else 1  # 1 for info/header sections
    return count


def _create_questions_from_sections(form, form_def):
    """Create FormQuestion rows from a form definition's sections."""
    order = 0
    question_map = {}

    for section in form_def.get('sections', []):
        section_number = section['number']
        section_title = section.get('title')
        section_description = section.get('description')
        is_repeatable = section.get('is_repeatable', False)
        section_group = section.get('section_group')
        min_repeats = section.get('min_repeats', 1)
        max_repeats = section.get('max_repeats', 10)

        # Build conditional rules for sections
        conditional_rules = None
        if section.get('conditional_on_section'):
            conditional_rules = {
                'type': 'section_conditional',
                'conditional_on_section': section.get('conditional_on_section'),
                'conditional_question': section.get('conditional_question'),
                'conditional_value': section.get('conditional_value')
            }

        for idx, q_data in enumerate(section.get('questions', [])):
            validation_rules = q_data.get('validation_rules', {}) or {}

            # Add section conditional rules to first question
            if idx == 0 and conditional_rules:
                validation_rules['section_conditional'] = conditional_rules

            question = FormQuestion(
                form_id=form.id,
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                is_required=q_data.get('is_required', False),
                allow_attachment=q_data.get('allow_attachment', False),
                options=q_data.get('options'),
                validation_rules=validation_rules if validation_rules else None,
                placeholder=q_data.get('placeholder'),
                help_text=q_data.get('help_text'),
                order=order,
                section_number=section_number,
                section_title=section_title if idx == 0 else None,
                section_description=section_description if idx == 0 else None,
                is_section_repeatable=is_repeatable,
                section_group=section_group,
                min_section_repeats=min_repeats,
                max_section_repeats=max_repeats
            )
            db.session.add(question)
            db.session.flush()
            question_map[q_data['question_text']] = question.id
            order += 1

        # If section has no questions (info section), add a placeholder
        if not section.get('questions'):
            validation_rules = {'type': 'section_header'}
            if conditional_rules:
                validation_rules['section_conditional'] = conditional_rules

            question = FormQuestion(
                form_id=form.id,
                question_text=section_title or 'Section Info',
                question_type='text',
                is_required=False,
                order=order,
                section_number=section_number,
                section_title=section_title,
                section_description=section_description,
                help_text=section_description,
                validation_rules=validation_rules
            )
            db.session.add(question)
            order += 1


def sync_form_service_links():
    """
    Ensure all forms in FORM_SERVICE_REGISTRY are linked to their services.
    Idempotent - safe to run multiple times.

    Returns:
        dict with 'linked', 'already_linked', 'missing_form', 'missing_service' counts
    """
    from app.modules.services.models import Service

    stats = {'linked': 0, 'already_linked': 0, 'missing_form': 0, 'missing_service': 0}

    for form_name, service_name in FORM_SERVICE_REGISTRY.items():
        form = Form.query.filter_by(name=form_name).first()
        service = Service.query.filter_by(name=service_name).first()

        if not form:
            print(f'  [WARN] Form "{form_name}" not found - skipping link')
            stats['missing_form'] += 1
            continue
        if not service:
            print(f'  [WARN] Service "{service_name}" not found - skipping link')
            stats['missing_service'] += 1
            continue

        if service.form_id == form.id:
            stats['already_linked'] += 1
            continue

        old_form_id = service.form_id
        service.form_id = form.id
        service.is_default = True
        stats['linked'] += 1
        if old_form_id:
            print(f'  [RELINK] "{service_name}": form_id {old_form_id} -> {form.id} ("{form_name}")')
        else:
            print(f'  [LINK] "{service_name}" -> "{form_name}" (form_id={form.id})')

    db.session.commit()
    return stats


def get_company_incorporation_form():
    """
    Returns the Company Incorporation Form definition.
    This form has 10 sections with repeatable director and shareholder sections.
    """
    return {
        'name': 'Company Incorporation Form',
        'description': 'Complete this form to register your new company with ASIC',
        'form_type': 'service',
        'sections': [
            {
                'number': 1,
                'title': 'Company Details',
                'description': 'Basic information about the new company',
                'questions': [
                    {
                        'question_text': 'Email',
                        'question_type': 'email',
                        'is_required': True,
                        'placeholder': 'contact@company.com',
                        'help_text': 'Primary contact email for this application'
                    },
                    {
                        'question_text': 'Proposed Name of the Company',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'Option 1: ABC Pty Ltd\nOption 2: XYZ Pty Ltd\nOption 3: DEF Pty Ltd',
                        'help_text': 'Provide 3 company names of your choice in the order of preference as ASIC will grant names based on availability'
                    },
                    {
                        'question_text': 'Main Business Activity Of the New Company',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'e.g., IT Consulting, Construction, Retail'
                    },
                    {
                        'question_text': 'Registered Office Address of the New Company',
                        'question_type': 'textarea',
                        'is_required': True,
                        'help_text': 'PO Box address will not work. This can be your home or business address. Note that ASIC charges a fee if you were to change the registered office address later'
                    },
                    {
                        'question_text': 'Principal Place of Business of the New Company',
                        'question_type': 'textarea',
                        'is_required': True,
                        'help_text': 'PO Box address will not work. This can be your home or business address. Note that ASIC charges a fee if you were to change the registered office address later'
                    }
                ]
            },
            {
                'number': 2,
                'title': 'New Company Directors\' Information',
                'description': 'Information about the directors of the new company',
                'questions': []  # This is an info section
            },
            {
                'number': 3,
                'title': 'Director Details',
                'description': 'Enter details for Director 1. Click "Add Another Director" to add more directors.',
                'is_repeatable': True,
                'section_group': 'director',
                'min_repeats': 1,
                'max_repeats': 10,
                'questions': [
                    {
                        'question_text': 'Full Name',
                        'question_type': 'text',
                        'is_required': True,
                        'help_text': 'Name should ideally be an exact match with a photo identity like passport or Drivers Licence and with ATO Records'
                    },
                    {
                        'question_text': 'Tax File Number (TFN)',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XXX XXX XXX'
                    },
                    {
                        'question_text': 'Director ID',
                        'question_type': 'text',
                        'is_required': True,
                        'help_text': 'Director Identification Number is pre-requisite for the incorporation of the company in Australia. If you do not have a Director ID, please apply online on www.abrs.gov.au/director-identification-number/apply-director-identification-number'
                    },
                    {
                        'question_text': 'Date of Birth',
                        'question_type': 'date',
                        'is_required': True
                    },
                    {
                        'question_text': 'Country of Birth',
                        'question_type': 'text',
                        'is_required': True
                    },
                    {
                        'question_text': 'City of Birth',
                        'question_type': 'text',
                        'is_required': True
                    },
                    {
                        'question_text': 'Mobile (Phone) Number',
                        'question_type': 'phone',
                        'is_required': True
                    },
                    {
                        'question_text': 'Email ID',
                        'question_type': 'email',
                        'is_required': True
                    },
                    {
                        'question_text': 'Residential Status (Australia)',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['PR (Permanent Resident)', 'Citizen', 'TR (Temporary Resident)', 'Non-resident'],
                        'help_text': 'Residential Status can be: PR, Citizen, TR, or non-resident'
                    },
                    {
                        'question_text': 'Residential Address (Australia)',
                        'question_type': 'textarea',
                        'is_required': True
                    },
                    {
                        'question_text': 'Director will also act as a:',
                        'question_type': 'multiselect',
                        'is_required': False,
                        'options': ['Public Officer', 'Secretary', 'None']
                    },
                    {
                        'question_text': 'Passport of Director',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Upload passport copy for this director'
                    },
                    {
                        'question_text': 'Drivers Licence of Director',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload drivers licence for this director (optional)'
                    }
                ]
            },
            {
                'number': 4,
                'title': 'Company\'s Shareholders Information',
                'description': 'Information about the shareholders of the new company',
                'questions': []  # This is an info section
            },
            {
                'number': 5,
                'title': 'Shareholder Details',
                'description': 'Enter details for Shareholder 1. Click "Add Another Shareholder" to add more shareholders.',
                'is_repeatable': True,
                'section_group': 'shareholder',
                'min_repeats': 1,
                'max_repeats': 10,
                'questions': [
                    {
                        'question_text': 'Full Name',
                        'question_type': 'text',
                        'is_required': True,
                        'help_text': 'Name should ideally be an exact match with a photo identity like passport or Drivers Licence and with ATO Records'
                    },
                    {
                        'question_text': 'Date of Birth',
                        'question_type': 'date',
                        'is_required': True
                    },
                    {
                        'question_text': 'Country of Birth',
                        'question_type': 'text',
                        'is_required': True
                    },
                    {
                        'question_text': 'City of Birth',
                        'question_type': 'text',
                        'is_required': True
                    },
                    {
                        'question_text': 'Mobile (Phone) Number',
                        'question_type': 'phone',
                        'is_required': True
                    },
                    {
                        'question_text': 'Email ID',
                        'question_type': 'email',
                        'is_required': True
                    },
                    {
                        'question_text': 'Residential Address (Australia)',
                        'question_type': 'textarea',
                        'is_required': True
                    },
                    {
                        'question_text': 'Percentage (%) of shares required in this new company',
                        'question_type': 'number',
                        'is_required': True,
                        'help_text': '% can be mentioned in numeric terms like 50%, 99% etc, but cannot exceed 100% combined for all shareholders',
                        'validation_rules': {'min': 0, 'max': 100}
                    },
                    {
                        'question_text': 'Passport of Shareholder',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Upload passport copy for this shareholder'
                    },
                    {
                        'question_text': 'Proof of Address',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload utility bill or bank statement for this shareholder (optional)'
                    }
                ]
            }
        ]
    }


def create_form_from_definition(form_def, creator_id=None):
    """
    Create a form with questions from a definition dictionary.
    Backward-compatible wrapper around upsert_form_from_definition.

    Args:
        form_def: Form definition dictionary
        creator_id: Optional user ID of the creator

    Returns:
        Created Form instance
    """
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def seed_company_incorporation_form(creator_id=None):
    """Seed the Company Incorporation form (idempotent)."""
    form_def = get_company_incorporation_form()
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def get_smsf_setup_form():
    """
    Returns the SMSF (Self-Managed Super Fund) Setup Form definition.
    This form has 7 sections with conditional logic for corporate trustee.
    """
    return {
        'name': 'SMSF Setup Form',
        'description': 'Complete this form to establish your Self-Managed Super Fund',
        'form_type': 'service',
        'sections': [
            {
                'number': 1,
                'title': 'SMSF Setup Details',
                'description': 'Basic information about your new SMSF',
                'questions': [
                    {
                        'question_text': 'Proposed Name of the SMSF Fund',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'e.g., Smith Family Superannuation Fund',
                        'help_text': 'Enter your preferred name for the SMSF'
                    },
                    {
                        'question_text': 'Registered Address',
                        'question_type': 'textarea',
                        'is_required': True,
                        'help_text': 'The official registered address for your SMSF'
                    },
                    {
                        'question_text': 'Principal Business Address',
                        'question_type': 'textarea',
                        'is_required': True,
                        'help_text': 'The main business address for your SMSF'
                    },
                    {
                        'question_text': 'Number of Members in SMSF',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['1', '2', '3', '4', '5', '6'],
                        'help_text': 'In case only 1 member is to be selected, please select "Corporate" as the trustee type in next question'
                    },
                    {
                        'question_text': 'Trustee Type',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Corporate', 'Individual'],
                        'help_text': 'Note: If it is a one member fund OR if you want to buy a property on loan through your SMSF, please select Corporate Trustee as an option'
                    }
                ]
            },
            {
                'number': 2,
                'title': 'Corporate Trustee (CT) Company Details',
                'description': 'Information about your Corporate Trustee Company',
                'questions': [
                    {
                        'question_text': 'Do you have an existing Corporate Trustee Company for your SMSF?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'Select Yes if you already have a company set up as trustee'
                    }
                ]
            },
            {
                'number': 3,
                'title': 'Existing Corporate Trustee Company Details',
                'description': 'Details of your existing Corporate Trustee Company',
                'conditional_on_section': 2,
                'conditional_question': 'Do you have an existing Corporate Trustee Company for your SMSF?',
                'conditional_value': 'Yes',
                'questions': [
                    {
                        'question_text': 'Full Name of Your existing Corporate Trustee Company',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'e.g., Smith Trustee Pty Ltd'
                    },
                    {
                        'question_text': 'ABN of your existing Corporate Trustee Company',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XX XXX XXX XXX'
                    }
                ]
            },
            {
                'number': 4,
                'title': 'New Corporate Trustee Company',
                'description': 'This section is to be filled when you do not have any existing Corporate Trustee Company for your SMSF and hence needs to be applied for',
                'conditional_on_section': 2,
                'conditional_question': 'Do you have an existing Corporate Trustee Company for your SMSF?',
                'conditional_value': 'No',
                'questions': [
                    {
                        'question_text': 'Proposed Company Name',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'Option 1: ABC Trustee Pty Ltd\nOption 2: XYZ Trustee Pty Ltd\nOption 3: DEF Trustee Pty Ltd',
                        'help_text': 'Give 3 names in the order of preference to check availability with ASIC'
                    }
                ]
            },
            {
                'number': 5,
                'title': 'Directors Details',
                'description': 'Details of corporate trustee company directors. Click "Add Another Director" if you have more than one director.',
                'is_repeatable': True,
                'section_group': 'director',
                'min_repeats': 1,
                'max_repeats': 6,
                'questions': [
                    {
                        'question_text': 'Director Name',
                        'question_type': 'text',
                        'is_required': True,
                        'help_text': 'Full legal name of the director'
                    },
                    {
                        'question_text': 'Director Residential Address',
                        'question_type': 'textarea',
                        'is_required': True,
                        'help_text': 'Current residential address of the director'
                    },
                    {
                        'question_text': 'Director ID',
                        'question_type': 'text',
                        'is_required': True,
                        'help_text': 'Director Identification Number. If you do not have one, apply at www.abrs.gov.au'
                    },
                    {
                        'question_text': 'Director Passport/ID Document',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Upload passport or government-issued ID for this director'
                    },
                    {
                        'question_text': 'Director Proof of Address',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload utility bill or bank statement showing address (optional)'
                    }
                ]
            },
            {
                'number': 6,
                'title': 'SMSF Members Details',
                'description': 'Enter details for Member 1. Click "Add Another Member" to add additional members if applicable.',
                'is_repeatable': True,
                'section_group': 'member',
                'min_repeats': 1,
                'max_repeats': 6,
                'questions': [
                    {
                        'question_text': 'Full Name',
                        'question_type': 'text',
                        'is_required': True,
                        'help_text': 'Full legal name as per identification documents'
                    },
                    {
                        'question_text': 'Residential Address',
                        'question_type': 'textarea',
                        'is_required': True,
                        'help_text': 'Current residential address'
                    },
                    {
                        'question_text': 'Tax File Number (TFN)',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XXX XXX XXX'
                    },
                    {
                        'question_text': 'Date of Birth',
                        'question_type': 'date',
                        'is_required': True
                    },
                    {
                        'question_text': 'Gender',
                        'question_type': 'select',
                        'is_required': False,
                        'options': ['Male', 'Female', 'Other', 'Prefer not to say']
                    },
                    {
                        'question_text': 'Member Passport/ID Document',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Upload passport or government-issued ID for this member'
                    },
                    {
                        'question_text': 'Member Proof of Address',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload utility bill or bank statement showing current address (optional)'
                    }
                ]
            },
            {
                'number': 7,
                'title': 'Other Information',
                'description': 'This section requires you to answer some other questions in relation to your SMSF Setup',
                'questions': [
                    {
                        'question_text': 'Do you want us to apply for opening Macquarie Bank Account for your SMSF as part of setup (at no additional cost)?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'This is an optional service only and you are free to choose a bank of your choice or preference. If this be the case, please select No while answering this question'
                    }
                ]
            }
        ]
    }


def seed_smsf_setup_form(creator_id=None):
    """Seed the SMSF Setup form (idempotent)."""
    form_def = get_smsf_setup_form()
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def get_smsf_annual_compliance_form():
    """
    Returns the SMSF Annual Compliance Client Questionnaire definition.
    This form collects annual compliance information from SMSF clients.
    """
    return {
        'name': 'SMSF Annual Compliance Questionnaire',
        'description': 'Annual compliance questionnaire for Self-Managed Super Fund clients',
        'form_type': 'service',
        'sections': [
            {
                'number': 1,
                'title': 'Fund Details',
                'description': 'Basic information about the SMSF',
                'questions': [
                    {
                        'question_text': 'What is the name of the SMSF?',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'e.g., Smith Family Superannuation Fund'
                    },
                    {
                        'question_text': 'What is the ABN of the SMSF?',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XX XXX XXX XXX'
                    },
                    {
                        'question_text': 'Financial year for this compliance?',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['2023-24', '2024-25', '2025-26', '2026-27']
                    },
                    {
                        'question_text': 'Does the fund have:',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Individual Trustees', 'Corporate Trustee']
                    }
                ]
            },
            {
                'number': 2,
                'title': 'Trustee & Member Information',
                'description': 'Details about trustees and members of the SMSF',
                'questions': [
                    {
                        'question_text': 'List all trustees/members of the SMSF',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'Enter full names of all trustees and members',
                        'help_text': 'Include full legal names of all trustees and members'
                    },
                    {
                        'question_text': 'Have there been any changes to trustees or members during the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'If yes, please describe the changes',
                        'question_type': 'textarea',
                        'is_required': False,
                        'placeholder': 'Describe any trustee or member changes',
                        'help_text': 'Only complete if you answered Yes above'
                    }
                ]
            },
            {
                'number': 3,
                'title': 'Bank Accounts',
                'description': 'Information about SMSF bank accounts',
                'questions': [
                    {
                        'question_text': 'How many SMSF bank accounts exist?',
                        'question_type': 'number',
                        'is_required': True,
                        'validation_rules': {'min': 1}
                    },
                    {
                        'question_text': 'Have you provided full-year bank statements (1 July – 30 June)?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    }
                ]
            },
            {
                'number': 4,
                'title': 'Contributions',
                'description': 'Details about contributions made during the year',
                'questions': [
                    {
                        'question_text': 'Did any member receive employer contributions during the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Did any member make personal (after-tax) contributions?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Were any contributions received late (after 30 June)?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No', 'Not sure']
                    }
                ]
            },
            {
                'number': 5,
                'title': 'Investments',
                'description': 'Information about SMSF investments',
                'questions': [
                    {
                        'question_text': 'Did the SMSF hold any of the following?',
                        'question_type': 'multiselect',
                        'is_required': True,
                        'options': [
                            'Listed shares / ETFs',
                            'Managed funds',
                            'Property',
                            'Term deposits',
                            'Cryptocurrency',
                            'Private companies / trusts',
                            'None of the above'
                        ]
                    },
                    {
                        'question_text': 'Were there any investment purchases or sales during the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Have you uploaded all buy/sell contracts and income statements?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    }
                ]
            },
            {
                'number': 6,
                'title': 'Property',
                'description': 'Complete this section if the SMSF owns property',
                'questions': [
                    {
                        'question_text': 'Does the SMSF own property?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Is the property:',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Residential', 'Commercial'],
                        'help_text': 'Only answer if the SMSF owns property'
                    },
                    {
                        'question_text': 'Have you provided the following property documents?',
                        'question_type': 'multiselect',
                        'is_required': False,
                        'options': [
                            'Rental statements',
                            'Expense invoices',
                            'Market valuation at 30 June'
                        ],
                        'help_text': 'Select all documents you have provided'
                    }
                ]
            },
            {
                'number': 7,
                'title': 'Pension Phase',
                'description': 'Information about pension payments',
                'questions': [
                    {
                        'question_text': 'Was any member in pension phase during the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Were minimum pension payments met?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No', 'Not sure'],
                        'help_text': 'Only answer if a member was in pension phase'
                    }
                ]
            },
            {
                'number': 8,
                'title': 'Compliance & Declarations',
                'description': 'Compliance questions and final declaration',
                'questions': [
                    {
                        'question_text': 'Were all investments made at arm\'s length?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No', 'Not sure'],
                        'help_text': 'Arm\'s length means transactions were conducted as if the parties were unrelated'
                    },
                    {
                        'question_text': 'Did the SMSF lend money to, or borrow from, related parties?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Do you confirm that all information provided is true and complete?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes'],
                        'help_text': 'You must confirm this declaration to submit the form'
                    }
                ]
            }
        ]
    }


def seed_smsf_annual_compliance_form(creator_id=None):
    """Seed the SMSF Annual Compliance form (idempotent)."""
    form_def = get_smsf_annual_compliance_form()
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def get_company_annual_compliance_form():
    """
    Returns the Company Annual Compliance Client Questionnaire definition.
    This form collects annual compliance information from company clients.
    """
    return {
        'name': 'Company Annual Compliance Questionnaire',
        'description': 'Annual compliance questionnaire for company clients',
        'form_type': 'service',
        'sections': [
            {
                'number': 1,
                'title': 'Company Information',
                'description': 'Basic company details',
                'questions': [
                    {
                        'question_text': 'Company legal name',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'e.g., ABC Pty Ltd'
                    },
                    {
                        'question_text': 'ACN',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XXX XXX XXX',
                        'help_text': 'Australian Company Number (9 digits)'
                    },
                    {
                        'question_text': 'Financial year',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['2023-24', '2024-25', '2025-26', '2026-27']
                    }
                ]
            },
            {
                'number': 2,
                'title': 'Directors & Shareholders',
                'description': 'Information about company directors and shareholders',
                'questions': [
                    {
                        'question_text': 'List all directors',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'Enter full names of all directors',
                        'help_text': 'Include full legal names of all current directors'
                    },
                    {
                        'question_text': 'List all shareholders and share percentages',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'e.g., John Smith - 50%, Jane Doe - 50%',
                        'help_text': 'Include name and percentage for each shareholder'
                    },
                    {
                        'question_text': 'Were there any changes to directors or shareholders?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    }
                ]
            },
            {
                'number': 3,
                'title': 'Accounting Records',
                'description': 'Information about your accounting software and records',
                'questions': [
                    {
                        'question_text': 'What accounting software do you use?',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['Xero', 'MYOB', 'QuickBooks', 'Excel', 'Other']
                    },
                    {
                        'question_text': 'Have you provided all bank statements for the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    }
                ]
            },
            {
                'number': 4,
                'title': 'Income',
                'description': 'Information about company income',
                'questions': [
                    {
                        'question_text': 'Primary source of business income',
                        'question_type': 'textarea',
                        'is_required': True,
                        'placeholder': 'Describe your main business activities and income sources'
                    },
                    {
                        'question_text': 'Did the company receive any other income?',
                        'question_type': 'multiselect',
                        'is_required': True,
                        'options': ['Interest', 'Grants', 'Asset sales', 'None']
                    }
                ]
            },
            {
                'number': 5,
                'title': 'Expenses',
                'description': 'Information about company expenses',
                'questions': [
                    {
                        'question_text': 'Have all business expenses been recorded?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Are there any private or mixed-use expenses?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'e.g., vehicle used for both business and personal purposes'
                    }
                ]
            },
            {
                'number': 6,
                'title': 'Payroll & Super',
                'description': 'Information about employees, payroll and superannuation',
                'questions': [
                    {
                        'question_text': 'Did the company have employees during the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Was Single Touch Payroll (STP) lodged for all pay runs?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No'],
                        'help_text': 'Only answer if the company had employees'
                    }
                ]
            },
            {
                'number': 7,
                'title': 'Loans & Dividends',
                'description': 'Information about loans and dividend payments',
                'questions': [
                    {
                        'question_text': 'Does the company owe money to any director or shareholder?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Does any director or shareholder owe money to the company?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'Division 7A loans may apply'
                    },
                    {
                        'question_text': 'Were dividends paid or declared during the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    }
                ]
            },
            {
                'number': 8,
                'title': 'ASIC & Tax',
                'description': 'ASIC and tax compliance questions',
                'questions': [
                    {
                        'question_text': 'Has the ASIC annual review fee been paid?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Have all BAS and IAS been lodged for the year?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'Business Activity Statements and Instalment Activity Statements'
                    }
                ]
            },
            {
                'number': 9,
                'title': 'Final Declaration',
                'description': 'Please confirm the accuracy of the information provided',
                'questions': [
                    {
                        'question_text': 'Do you confirm the information provided is complete and accurate?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes'],
                        'help_text': 'You must confirm this declaration to submit the form'
                    }
                ]
            }
        ]
    }


def seed_company_annual_compliance_form(creator_id=None):
    """Seed the Company Annual Compliance form (idempotent)."""
    form_def = get_company_annual_compliance_form()
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def get_smsf_annual_audit_form():
    """
    Returns the SMSF Annual Audit Form definition.
    This comprehensive form collects all documents and information required
    for conducting an annual SMSF audit as per Australian regulations.

    Based on ATO SMSF Auditor checklist and industry best practices.
    Reference: https://www.ato.gov.au/tax-and-super-professionals/for-superannuation-professionals/smsf-auditors/auditing-an-smsf
    """
    return {
        'name': 'SMSF Annual Audit Form',
        'description': 'Complete this form and upload all required documents for your SMSF Annual Audit. All assets must be valued at market value as at 30 June.',
        'form_type': 'service',
        'sections': [
            {
                'number': 1,
                'title': 'Fund Information',
                'description': 'Basic details about the SMSF being audited',
                'questions': [
                    {
                        'question_text': 'Name of the SMSF',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'e.g., Smith Family Superannuation Fund'
                    },
                    {
                        'question_text': 'ABN of the SMSF',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XX XXX XXX XXX'
                    },
                    {
                        'question_text': 'Financial Year End Date',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['30 June 2024', '30 June 2025', '30 June 2026', '30 June 2027'],
                        'help_text': 'Select the financial year being audited'
                    },
                    {
                        'question_text': 'Trustee Structure',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Individual Trustees', 'Corporate Trustee'],
                        'help_text': 'Select the type of trustee structure for your SMSF'
                    },
                    {
                        'question_text': 'Number of Members',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['1', '2', '3', '4', '5', '6']
                    }
                ]
            },
            {
                'number': 2,
                'title': 'Governing Documents (Permanent Files)',
                'description': 'Upload the governing documents of your SMSF. These documents establish and govern the operation of your fund.',
                'questions': [
                    {
                        'question_text': 'Trust Deed (including all amendments)',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Upload the current Trust Deed and any amendments made since establishment'
                    },
                    {
                        'question_text': 'Investment Strategy (current)',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Must be reviewed annually and reflect actual investments held. Should consider risk, return, liquidity, diversification, and insurance needs of members.'
                    },
                    {
                        'question_text': 'Trustee Declarations (all trustees)',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'ATO Trustee Declaration forms signed by all trustees within 21 days of appointment'
                    },
                    {
                        'question_text': 'Trustee/Member Consent Forms',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Consent to act as trustee and member of the SMSF'
                    },
                    {
                        'question_text': 'Minutes of Trustee Meetings (for the financial year)',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Include minutes for investment decisions, pension commencement, contributions acceptance, etc.'
                    },
                    {
                        'question_text': 'ASIC Company Extract (for Corporate Trustee only)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Current ASIC extract showing directors and shareholders of the corporate trustee company'
                    }
                ]
            },
            {
                'number': 3,
                'title': 'Financial Statements & Tax Records',
                'description': 'Provide the financial statements and tax records for the audit year',
                'questions': [
                    {
                        'question_text': 'Financial Statements (Balance Sheet & Operating Statement)',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Includes Statement of Financial Position (Balance Sheet) and Operating Statement (Profit & Loss) for the financial year'
                    },
                    {
                        'question_text': 'Member Statements',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Individual member account balances and movement summaries'
                    },
                    {
                        'question_text': 'General Ledger / Trial Balance',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Detailed transaction listing for the financial year'
                    },
                    {
                        'question_text': 'Prior Year Audit Report',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Previous year\'s Independent Auditor\'s Report (if not first year audit)'
                    },
                    {
                        'question_text': 'Prior Year Tax Return',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Previous year\'s SMSF Annual Return lodged with ATO'
                    },
                    {
                        'question_text': 'ATO Rollover Benefit Statements (if applicable)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'For any rollovers received during the year'
                    }
                ]
            },
            {
                'number': 4,
                'title': 'Bank Account Records',
                'description': 'Provide complete bank records for ALL SMSF bank accounts',
                'questions': [
                    {
                        'question_text': 'How many bank accounts does the SMSF have?',
                        'question_type': 'number',
                        'is_required': True,
                        'validation_rules': {'min': 1},
                        'help_text': 'Include cash management accounts, term deposits held at banks, etc.'
                    },
                    {
                        'question_text': 'Bank Statements (Full Year: 1 July to 30 June)',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Complete bank statements for ALL SMSF accounts covering the entire financial year. Must show opening and closing balances.',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Bank Reconciliation at 30 June',
                        'question_type': 'file',
                        'is_required': True,
                        'help_text': 'Bank reconciliation showing outstanding items at year end'
                    },
                    {
                        'question_text': 'Term Deposit Statements/Certificates',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload if the SMSF holds term deposits'
                    },
                    {
                        'question_text': 'Is the bank account held in the name of the SMSF (not personal names)?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'SMSF funds must not be mixed with personal funds'
                    }
                ]
            },
            {
                'number': 5,
                'title': 'Listed Investments (Shares, ETFs, Managed Funds)',
                'description': 'Provide records for all listed investments held by the SMSF',
                'questions': [
                    {
                        'question_text': 'Does the SMSF hold listed shares, ETFs, or managed funds?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Share/Investment Portfolio Report at 30 June',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Portfolio valuation showing all holdings and market values at 30 June'
                    },
                    {
                        'question_text': 'Buy/Sell Contract Notes (for transactions during the year)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Contract notes for all share purchases and sales during the financial year',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Dividend Statements',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Dividend statements and Distribution statements received during the year',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Corporate Actions Documentation',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Documentation for share splits, buy-backs, mergers, etc. if applicable'
                    },
                    {
                        'question_text': 'CHESS Holding Statements',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'CHESS statements showing share ownership registration'
                    }
                ]
            },
            {
                'number': 6,
                'title': 'Property Investments',
                'description': 'Complete this section if the SMSF owns real property (residential or commercial)',
                'questions': [
                    {
                        'question_text': 'Does the SMSF own property?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Property Type',
                        'question_type': 'select',
                        'is_required': False,
                        'options': ['Residential', 'Commercial', 'Both Residential and Commercial'],
                        'help_text': 'Note: Residential property cannot be lived in by members or related parties'
                    },
                    {
                        'question_text': 'Certificate of Title / Title Search',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Current title search showing SMSF/trustee as registered owner (required every 3 years minimum)'
                    },
                    {
                        'question_text': 'Purchase Contract and Settlement Statement',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Required if property was purchased during the audit year'
                    },
                    {
                        'question_text': 'Property Valuation at 30 June (Market Value)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Independent valuation or evidence supporting market value at year end. For 2025 and beyond, valuations are critical due to proposed Div 296 tax on balances over $3M.'
                    },
                    {
                        'question_text': 'Rental/Lease Agreements',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Current lease agreement with tenant'
                    },
                    {
                        'question_text': 'Property Management Statements',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Statements from property manager showing rental income and expenses',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Property Expense Invoices (Insurance, Rates, Repairs)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Council rates, water rates, insurance, repairs, and maintenance invoices',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Is the property leased to a related party?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes - Business Real Property', 'No'],
                        'help_text': 'Related party leasing is only permitted for business real property at market rent'
                    }
                ]
            },
            {
                'number': 7,
                'title': 'Limited Recourse Borrowing Arrangement (LRBA)',
                'description': 'Complete if the SMSF has borrowed money to purchase assets',
                'questions': [
                    {
                        'question_text': 'Does the SMSF have a Limited Recourse Borrowing Arrangement (LRBA)?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Loan Agreement',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'LRBA loan agreement document'
                    },
                    {
                        'question_text': 'Bare Trust Deed',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Holding trust/bare trust deed for the LRBA asset'
                    },
                    {
                        'question_text': 'Loan Statements (Full Year)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Loan statements showing principal and interest payments for the year',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Is the LRBA from a related party?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No'],
                        'help_text': 'Related party LRBAs must comply with ATO safe harbour terms'
                    }
                ]
            },
            {
                'number': 8,
                'title': 'Private Company & Trust Investments',
                'description': 'Complete if the SMSF holds investments in unlisted/private companies or trusts',
                'questions': [
                    {
                        'question_text': 'Does the SMSF hold investments in private companies or trusts?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Share/Unit Certificates',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Certificates showing ownership of shares in private companies or units in trusts'
                    },
                    {
                        'question_text': 'Financial Statements of Private Entity',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Audited or reviewed financial statements of the private company/trust',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Tax Returns of Private Entity',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Income tax returns of the private company/trust'
                    },
                    {
                        'question_text': 'Valuation of Private Investment at 30 June',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Documentation supporting the market value of private investments'
                    },
                    {
                        'question_text': 'Is the private entity a related party of the SMSF?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No'],
                        'help_text': 'In-house asset rules may apply to related party investments'
                    }
                ]
            },
            {
                'number': 9,
                'title': 'Cryptocurrency & Other Assets',
                'description': 'Complete if the SMSF holds cryptocurrency or other alternative investments',
                'questions': [
                    {
                        'question_text': 'Does the SMSF hold cryptocurrency?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Cryptocurrency Exchange Statements',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Full year statements from crypto exchanges showing holdings and transactions'
                    },
                    {
                        'question_text': 'Cryptocurrency Wallet Holdings at 30 June',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Screenshot or export of wallet holdings with market values at 30 June'
                    },
                    {
                        'question_text': 'Does the SMSF hold any other alternative investments?',
                        'question_type': 'multiselect',
                        'is_required': True,
                        'options': [
                            'Collectibles (art, wine, etc.)',
                            'Precious metals (gold, silver)',
                            'Foreign assets',
                            'Options/Derivatives',
                            'None of the above'
                        ],
                        'help_text': 'Note: Collectibles and personal use assets have strict storage and insurance requirements'
                    },
                    {
                        'question_text': 'Other Asset Documentation',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Provide valuations and ownership documents for any other assets held',
                        'allow_attachment': True
                    }
                ]
            },
            {
                'number': 10,
                'title': 'Contributions',
                'description': 'Information about contributions received during the financial year',
                'questions': [
                    {
                        'question_text': 'Types of contributions received during the year',
                        'question_type': 'multiselect',
                        'is_required': True,
                        'options': [
                            'Employer (SG) contributions',
                            'Salary sacrifice contributions',
                            'Personal deductible contributions',
                            'Non-concessional (after-tax) contributions',
                            'Spouse contributions',
                            'Downsizer contributions',
                            'Government co-contributions',
                            'Rollovers from other funds',
                            'No contributions received'
                        ]
                    },
                    {
                        'question_text': 'Contribution Receipts/Remittance Advices',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Documentation showing contributions received and their classification',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Section 290-170 Notices (Notice of Intent to Claim Deduction)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Required for personal contributions claimed as tax deductions'
                    },
                    {
                        'question_text': 'Were all contributions received within 28 days of the contribution date?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No', 'Not sure'],
                        'help_text': 'Contributions must be allocated within 28 days of receipt'
                    },
                    {
                        'question_text': 'Any ATO Notices received (Div 293, Excess Contributions, etc.)?',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload any ATO determination notices received',
                        'allow_attachment': True
                    }
                ]
            },
            {
                'number': 11,
                'title': 'Pension Payments',
                'description': 'Complete if any member is receiving a pension from the SMSF',
                'questions': [
                    {
                        'question_text': 'Is any member receiving a pension from the SMSF?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Pension Type',
                        'question_type': 'multiselect',
                        'is_required': False,
                        'options': [
                            'Account-based pension',
                            'Transition to retirement pension',
                            'Death benefit pension',
                            'Disability pension'
                        ]
                    },
                    {
                        'question_text': 'Pension Commencement Documentation',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Trustee minutes and member election to commence pension'
                    },
                    {
                        'question_text': 'Were minimum pension payments made for the year?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No'],
                        'help_text': 'Minimum pension must be paid by 30 June to retain pension tax exemption'
                    },
                    {
                        'question_text': 'Actuarial Certificate (if required)',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Required if the fund has both accumulation and pension members to determine tax-exempt proportion'
                    }
                ]
            },
            {
                'number': 12,
                'title': 'Insurance',
                'description': 'Details of insurance policies held within the SMSF',
                'questions': [
                    {
                        'question_text': 'Does the SMSF provide insurance for any members?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Types of insurance held',
                        'question_type': 'multiselect',
                        'is_required': False,
                        'options': [
                            'Life insurance',
                            'Total & Permanent Disability (TPD)',
                            'Income protection',
                            'None'
                        ]
                    },
                    {
                        'question_text': 'Insurance Policy Documents/Certificates',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Current insurance policy certificates',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'Has the consideration of insurance been documented in minutes?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No'],
                        'help_text': 'Trustees must consider insurance needs when formulating investment strategy'
                    }
                ]
            },
            {
                'number': 13,
                'title': 'Compliance Questions',
                'description': 'Important compliance questions for the SMSF audit',
                'questions': [
                    {
                        'question_text': 'Have all investments been made on an arm\'s length basis?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No', 'Not sure'],
                        'help_text': 'All transactions must be at market value as if dealing with unrelated parties'
                    },
                    {
                        'question_text': 'Has the SMSF acquired any assets from related parties?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'Only business real property and listed securities can generally be acquired from related parties'
                    },
                    {
                        'question_text': 'Has the SMSF provided financial assistance to members or relatives?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'Loans to members or relatives are prohibited'
                    },
                    {
                        'question_text': 'Are all assets held in the name of the SMSF trustees?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'Assets must be held in trustee names and kept separate from personal assets'
                    },
                    {
                        'question_text': 'Have all trustees met their trustee declaration obligations?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Is the fund\'s sole purpose to provide retirement benefits to members?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No'],
                        'help_text': 'The sole purpose test is fundamental to SMSF compliance'
                    }
                ]
            },
            {
                'number': 14,
                'title': 'Additional Information & Declaration',
                'description': 'Any additional information and final declaration',
                'questions': [
                    {
                        'question_text': 'Are there any matters the auditor should be aware of?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'placeholder': 'Describe any unusual transactions, changes to the fund, or other relevant information...',
                        'help_text': 'Include any significant events, contraventions, or matters requiring attention'
                    },
                    {
                        'question_text': 'Other Supporting Documents',
                        'question_type': 'file',
                        'is_required': False,
                        'help_text': 'Upload any other documents relevant to the audit',
                        'allow_attachment': True
                    },
                    {
                        'question_text': 'I confirm that all information provided is true and complete to the best of my knowledge',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes, I confirm'],
                        'help_text': 'This declaration is required to submit the audit documents'
                    },
                    {
                        'question_text': 'I understand that the auditor may request additional information if required',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes, I understand'],
                        'help_text': 'The auditor must be provided all requested documents within 14 days'
                    }
                ]
            }
        ]
    }


def seed_smsf_annual_audit_form(creator_id=None):
    """Seed the SMSF Annual Audit form (idempotent)."""
    form_def = get_smsf_annual_audit_form()
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def get_individual_tax_return_form():
    """
    Returns the Individual Tax Return (ITR) Form definition.
    This comprehensive form has 7 sections covering personal info, Medicare/ABN,
    spouse details, capital gains, income sources, deductions, and document uploads.
    """
    return {
        'name': 'Individual Tax Return Form',
        'description': 'Complete this form to provide all required information for your Individual Tax Return',
        'form_type': 'service',
        'sections': [
            {
                'number': 1,
                'title': 'Personal Information',
                'description': 'Basic personal and income details',
                'questions': [
                    {
                        'question_text': 'What is your Tax File Number (TFN)?',
                        'question_type': 'text',
                        'is_required': True,
                        'placeholder': 'XXX XXX XXX'
                    },
                    {
                        'question_text': 'What is your date of birth?',
                        'question_type': 'date',
                        'is_required': True
                    },
                    {
                        'question_text': 'What is your occupation?',
                        'question_type': 'text',
                        'is_required': True
                    },
                    {
                        'question_text': 'Did you have any income from employment?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Did you have any bank interest income?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Did you have any dividend income?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Do you have private health insurance?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'What work-related expenses do you want to claim?',
                        'question_type': 'multiselect',
                        'is_required': False,
                        'options': [
                            'Work from home expenses',
                            'Vehicle/Travel expenses',
                            'Uniform/Clothing',
                            'Tools and equipment',
                            'Self-education',
                            'Other'
                        ]
                    }
                ]
            },
            {
                'number': 2,
                'title': 'Medicare & ABN',
                'description': 'Medicare and self-employment details',
                'questions': [
                    {
                        'question_text': 'Do you have a Medicare Card?',
                        'question_type': 'select',
                        'is_required': True,
                        'options': ['Yes', 'No', 'Medicare Levy Exempt']
                    },
                    {
                        'question_text': 'Are you self employed/sub-contractor/work under your own ABN?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Provide details if you are self-employed or work as a sub-contractor'
                    },
                    {
                        'question_text': 'Your ABN number?',
                        'question_type': 'text',
                        'is_required': False,
                        'placeholder': 'XX XXX XXX XXX',
                        'help_text': 'If No ABN, write "Not Applicable"'
                    }
                ]
            },
            {
                'number': 3,
                'title': 'Spouse Details',
                'description': 'Information about your spouse (if applicable)',
                'questions': [
                    {
                        'question_text': 'Do you have a spouse?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Is your spouse a Pointers Consulting existing client?',
                        'question_type': 'radio',
                        'is_required': False,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Spouse Full Name',
                        'question_type': 'text',
                        'is_required': False
                    },
                    {
                        'question_text': 'Spouse Date of Birth',
                        'question_type': 'date',
                        'is_required': False
                    },
                    {
                        'question_text': 'Spouse TFN',
                        'question_type': 'text',
                        'is_required': False,
                        'placeholder': 'XXX XXX XXX'
                    },
                    {
                        'question_text': 'Spouse Gross Taxable Income ($)',
                        'question_type': 'number',
                        'is_required': False,
                        'placeholder': '0.00'
                    },
                    {
                        'question_text': 'Any dependents?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'List all dependents with their name, date of birth and relationship'
                    }
                ]
            },
            {
                'number': 4,
                'title': 'Capital Gains Tax Information',
                'description': 'Details about asset sales during the financial year',
                'questions': [
                    {
                        'question_text': 'Did you SELL any Assets (like units of Shares/Crypto/Land/House during this FY)?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'List all such assets sold?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Provide details of each asset sold including type, purchase date, sale date, purchase price and sale price'
                    }
                ]
            },
            {
                'number': 5,
                'title': 'Income Sources',
                'description': 'Other income sources beyond salary',
                'questions': [
                    {
                        'question_text': 'Do you have any Investment Property generating rental income for you during this FY?',
                        'question_type': 'radio',
                        'is_required': True,
                        'options': ['Yes', 'No']
                    },
                    {
                        'question_text': 'Please provide full address of each such investment property',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'List the full address of each investment property'
                    },
                    {
                        'question_text': 'Do you earn any other income other than salary?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'E.g. freelance income, foreign income, government payments, etc.'
                    }
                ]
            },
            {
                'number': 6,
                'title': 'Personal Expense Deductions',
                'description': 'Provide details and amounts for all deductions you wish to claim',
                'questions': [
                    {
                        'question_text': 'Work from Home Expenses',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Details and amounts of work from home expenses'
                    },
                    {
                        'question_text': 'Home Office Set-up',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Details and amounts of home office setup costs'
                    },
                    {
                        'question_text': 'Educational expenses',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Self-education expenses related to your current employment'
                    },
                    {
                        'question_text': 'Work Related Car Expenses',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Details of work-related car travel (not home to work commute)'
                    },
                    {
                        'question_text': 'Travel Expenses',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Work-related travel expenses (flights, accommodation, meals)'
                    },
                    {
                        'question_text': 'Uniform/Laundry Expenses',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Occupation-specific clothing, protective clothing, or compulsory uniform expenses'
                    },
                    {
                        'question_text': 'Union/Annual Membership Fees paid',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Union fees, professional association memberships'
                    },
                    {
                        'question_text': 'Donations to approved Charities',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Donations of $2 or more to registered Deductible Gift Recipients (DGR)'
                    },
                    {
                        'question_text': 'Tax Agent Fee',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Fee paid to tax agent for preparing previous year tax return'
                    },
                    {
                        'question_text': 'Income Protection Insurance',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Income protection insurance premiums paid'
                    },
                    {
                        'question_text': 'Tools, Equipment, or any asset purchased',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Work-related tools, equipment, or assets purchased during the year'
                    },
                    {
                        'question_text': 'Any other Deductions',
                        'question_type': 'textarea',
                        'is_required': False,
                        'help_text': 'Any other deductions not listed above'
                    }
                ]
            },
        ]
    }


def seed_individual_tax_return_form(creator_id=None):
    """Seed the Individual Tax Return form (idempotent)."""
    form_def = get_individual_tax_return_form()
    form, _ = upsert_form_from_definition(form_def, creator_id)
    return form


def seed_all_service_forms(creator_id=None):
    """
    Seed all service-specific forms and sync form-service links.

    This is idempotent:
    - New forms are created, existing forms are updated (if no responses)
    - Service-to-form links are synced from FORM_SERVICE_REGISTRY
    - Safe to run on every deploy / app startup
    """
    print('\n=== Seeding comprehensive service forms ===')
    seed_company_incorporation_form(creator_id)
    seed_smsf_setup_form(creator_id)
    seed_smsf_annual_compliance_form(creator_id)
    seed_company_annual_compliance_form(creator_id)
    seed_smsf_annual_audit_form(creator_id)
    seed_individual_tax_return_form(creator_id)
    # Add more forms here as needed

    print('\n=== Syncing form-service links ===')
    stats = sync_form_service_links()
    print(f'  Links: {stats["linked"]} new, {stats["already_linked"]} unchanged, '
          f'{stats["missing_form"]} missing forms, {stats["missing_service"]} missing services')
    print('=== Form seeding complete ===\n')
