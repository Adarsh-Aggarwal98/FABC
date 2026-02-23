"""
Auth Schemas - Request/response validation for authentication endpoints
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
import re


def validate_email_format(email):
    """Simple email format validation without DNS check"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Invalid email format')


class LoginSchema(Schema):
    """Schema for login request"""
    email = fields.Str(required=True, validate=validate_email_format)
    password = fields.Str(required=True, load_only=True)


class VerifyOTPSchema(Schema):
    """Schema for OTP verification"""
    email = fields.Str(required=True, validate=validate_email_format)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request"""
    email = fields.Str(required=True, validate=validate_email_format)


class ResetPasswordSchema(Schema):
    """Schema for password reset"""
    email = fields.Str(required=True, validate=validate_email_format)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))
    new_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True, load_only=True)
