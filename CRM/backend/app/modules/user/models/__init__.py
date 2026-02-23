"""
User Models Package

This module exports all models for the user module.
Import models from here for backward compatibility:
    from app.modules.user.models import User, Role, OTP, ClientNote
"""

from .user import User
from .role import Role
from .otp import OTP
from .client_note import ClientNote

__all__ = [
    'User',
    'Role',
    'OTP',
    'ClientNote',
]
