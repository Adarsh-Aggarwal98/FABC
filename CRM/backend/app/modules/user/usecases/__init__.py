"""
User Use Cases Package

This module exports all use cases for the user module.
Import use cases from here for backward compatibility:
    from app.modules.user.usecases import LoginUseCase, InviteUserUseCase
"""

# Auth Use Cases
from .auth import (
    LoginUseCase,
    VerifyOTPUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
)

# User Management Use Cases
from .users import (
    InviteUserUseCase,
    CompleteOnboardingUseCase,
    UpdateProfileUseCase,
    ChangePasswordUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    ToggleUserStatusUseCase,
    GetAccountantsUseCase,
    CheckDuplicatesUseCase,
)

# Client Notes Use Cases
from .notes import (
    GetClientNotesUseCase,
    CreateClientNoteUseCase,
    UpdateClientNoteUseCase,
    DeleteClientNoteUseCase,
    ToggleNotePinUseCase,
)

__all__ = [
    # Auth
    'LoginUseCase',
    'VerifyOTPUseCase',
    'ForgotPasswordUseCase',
    'ResetPasswordUseCase',
    # User Management
    'InviteUserUseCase',
    'CompleteOnboardingUseCase',
    'UpdateProfileUseCase',
    'ChangePasswordUseCase',
    'GetUserUseCase',
    'ListUsersUseCase',
    'ToggleUserStatusUseCase',
    'GetAccountantsUseCase',
    'CheckDuplicatesUseCase',
    # Client Notes
    'GetClientNotesUseCase',
    'CreateClientNoteUseCase',
    'UpdateClientNoteUseCase',
    'DeleteClientNoteUseCase',
    'ToggleNotePinUseCase',
]
