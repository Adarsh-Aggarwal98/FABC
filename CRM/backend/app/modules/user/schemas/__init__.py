"""
User Schemas Package

This module exports all schemas for the user module.
Import schemas from here for backward compatibility:
    from app.modules.user.schemas import LoginSchema, UserSchema
"""

# Auth Schemas
from .auth_schemas import (
    LoginSchema,
    VerifyOTPSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    validate_email_format,
)

# User Schemas
from .user_schemas import (
    InviteUserSchema,
    UpdatePasswordSchema,
    StaffOnboardingSchema,
    OnboardingSchema,
    UpdateProfileSchema,
    UserSchema,
    UserListSchema,
)

__all__ = [
    # Auth
    'LoginSchema',
    'VerifyOTPSchema',
    'ForgotPasswordSchema',
    'ResetPasswordSchema',
    'validate_email_format',
    # User
    'InviteUserSchema',
    'UpdatePasswordSchema',
    'StaffOnboardingSchema',
    'OnboardingSchema',
    'UpdateProfileSchema',
    'UserSchema',
    'UserListSchema',
]
