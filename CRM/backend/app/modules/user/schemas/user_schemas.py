"""
User Schemas - Request/response validation for user management endpoints
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
import re


def validate_email_format(email):
    """Simple email format validation without DNS check"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Invalid email format')


class InviteUserSchema(Schema):
    """Schema for inviting a new user"""
    email = fields.Str(required=True, validate=validate_email_format)
    # Allow super_admin in schema - route logic will check permissions
    role = fields.Str(required=True, validate=validate.OneOf(['super_admin', 'admin', 'senior_accountant', 'accountant', 'external_accountant', 'user']))
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    company_id = fields.Str()  # Optional - Super Admin can specify company
    supervisor_id = fields.Str()  # Optional - For accountants, assign to a senior accountant


class UpdatePasswordSchema(Schema):
    """Schema for updating password"""
    current_password = fields.Str(required=False, load_only=True)
    new_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True, load_only=True)

    @validates('new_password')
    def validate_password(self, value, **kwargs):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        if not any(c.isupper() for c in value):
            raise ValidationError('Password must contain uppercase letter')
        if not any(c.islower() for c in value):
            raise ValidationError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in value):
            raise ValidationError('Password must contain a digit')


class StaffOnboardingSchema(Schema):
    """Schema for staff (admin/accountant) onboarding - simplified form with password and personal info only"""
    # Step 1: Change password
    new_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True, load_only=True)

    # Step 2: Personal Information
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(required=True, validate=validate.Length(max=20))  # Mobile number
    personal_email = fields.Str(validate=validate_email_format)  # Personal email (not official)
    address = fields.Str(required=True)  # Current residential address

    # Terms implicitly accepted for staff
    terms_accepted = fields.Bool(load_default=True)

    @validates('new_password')
    def validate_password(self, value, **kwargs):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        if not any(c.isupper() for c in value):
            raise ValidationError('Password must contain uppercase letter')
        if not any(c.islower() for c in value):
            raise ValidationError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in value):
            raise ValidationError('Password must contain a digit')


class OnboardingSchema(Schema):
    """Schema for completing onboarding - multi-step form for clients"""
    # Step 1: Change password
    new_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True, load_only=True)

    # Step 2: Personal Information
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(required=True, validate=validate.Length(max=20))  # Mobile number
    personal_email = fields.Str(validate=validate_email_format)  # Personal email (not official)
    address = fields.Str(required=True)  # Current residential address
    visa_status = fields.Str(required=True, validate=validate.OneOf([
        'citizen', 'permanent_resident', 'temporary_resident',
        'working_holiday', 'student', 'other'
    ]))

    # Step 3: Additional Details
    tfn = fields.Str(required=True, validate=validate.Length(max=20))  # Tax File Number
    date_of_birth = fields.Date(required=True)
    occupation = fields.Str(required=True, validate=validate.Length(max=100))

    # Step 4: Bank Account Details
    bsb = fields.Str(required=True, validate=validate.Length(max=10))
    bank_account_number = fields.Str(required=True, validate=validate.Length(max=20))
    bank_account_holder_name = fields.Str(required=True, validate=validate.Length(max=100))

    # Document URLs (uploaded to SharePoint)
    id_document_url = fields.Str(load_default=None)
    passport_url = fields.Str(load_default=None)
    bank_statement_url = fields.Str(load_default=None)
    driving_licence_url = fields.Str(load_default=None)

    # Step 5: Terms & Conditions
    terms_accepted = fields.Bool(required=True)

    # Optional: Service selection (may be done separately)
    company_name = fields.Str(validate=validate.Length(max=100))
    service_ids = fields.List(fields.Int())

    @validates('new_password')
    def validate_password(self, value, **kwargs):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        if not any(c.isupper() for c in value):
            raise ValidationError('Password must contain uppercase letter')
        if not any(c.islower() for c in value):
            raise ValidationError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in value):
            raise ValidationError('Password must contain a digit')

    @validates('terms_accepted')
    def validate_terms(self, value, **kwargs):
        if not value:
            raise ValidationError('You must accept the terms and conditions')


class UpdateProfileSchema(Schema):
    """Schema for updating user profile"""
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    address = fields.Str()
    company_name = fields.Str(validate=validate.Length(max=100))
    personal_email = fields.Str(validate=validate_email_format)
    date_of_birth = fields.Date()
    occupation = fields.Str(validate=validate.Length(max=100))
    visa_status = fields.Str(validate=validate.OneOf([
        'citizen', 'permanent_resident', 'temporary_resident',
        'working_holiday', 'student', 'other'
    ]))
    # Document URLs (document IDs from upload)
    id_document_url = fields.Str(load_default=None)
    passport_url = fields.Str(load_default=None)
    bank_statement_url = fields.Str(load_default=None)
    driving_licence_url = fields.Str(load_default=None)


class UserSchema(Schema):
    """Schema for user response"""
    id = fields.Str(dump_only=True)
    email = fields.Str(validate=validate_email_format)
    first_name = fields.Str()
    last_name = fields.Str()
    full_name = fields.Str(dump_only=True)
    phone = fields.Str()
    address = fields.Str()
    company_name = fields.Str()
    role = fields.Str(attribute='role.name')
    is_active = fields.Bool()
    is_verified = fields.Bool()
    is_first_login = fields.Bool()
    created_at = fields.DateTime()
    last_login = fields.DateTime()


class UserListSchema(Schema):
    """Schema for user list response"""
    id = fields.Str()
    email = fields.Str(validate=validate_email_format)
    full_name = fields.Str()
    role = fields.Str(attribute='role.name')
    is_active = fields.Bool()
    created_at = fields.DateTime()
