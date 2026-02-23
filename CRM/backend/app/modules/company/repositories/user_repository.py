"""
User Repository - Data Access Layer
====================================

Repository for User entity with custom queries.
Note: This is in the company module for convenience but operates on User model.
"""
from typing import Optional
from app.common.repository import BaseRepository
from app.modules.user.models import User


class UserRepository(BaseRepository[User]):
    """Repository with custom User queries"""
    model = User

    def email_exists(self, email: str) -> bool:
        """Check if email exists (case-insensitive)"""
        return self.exists(email=email.lower().strip())

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email (case-insensitive)"""
        return self.find_by(email=email.lower().strip())
