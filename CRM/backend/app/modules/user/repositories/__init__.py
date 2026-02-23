"""
User Repositories Package

This module exports all repositories for the user module.
Import repositories from here:
    from app.modules.user.repositories import UserRepository, RoleRepository
"""

from .user_repository import UserRepository
from .role_repository import RoleRepository
from .otp_repository import OTPRepository
from .client_note_repository import ClientNoteRepository

__all__ = [
    'UserRepository',
    'RoleRepository',
    'OTPRepository',
    'ClientNoteRepository',
]
