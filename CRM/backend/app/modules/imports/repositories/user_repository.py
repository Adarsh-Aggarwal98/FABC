"""
User Repository for Import Operations

Provides data access methods for user-related import operations.
"""
import logging
from typing import Optional, Dict
from datetime import date

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.modules.user.models import User, Role

logger = logging.getLogger(__name__)


class UserImportRepository:
    """Repository for user import operations."""

    @staticmethod
    def get_client_role() -> Optional[Role]:
        """Get the client/user role."""
        return Role.query.filter_by(name='user').first()

    @staticmethod
    def get_admin_role() -> Optional[Role]:
        """Get the admin role."""
        return Role.query.filter_by(name='admin').first()

    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if a user with the given email exists."""
        return User.query.filter_by(email=email.lower()).first() is not None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get a user by email."""
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def get_users_by_company(company_id: int) -> Dict[str, User]:
        """Get all users for a company, indexed by lowercase email."""
        users = User.query.filter_by(company_id=company_id).all()
        return {user.email.lower(): user for user in users}

    @staticmethod
    def create_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: Role,
        company_id: int,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        occupation: Optional[str] = None,
        company_name: Optional[str] = None,
        abn: Optional[str] = None,
        tfn: Optional[str] = None,
        personal_email: Optional[str] = None,
        bsb: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        bank_account_holder_name: Optional[str] = None,
        is_first_login: bool = True
    ) -> User:
        """
        Create a new user.

        Args:
            email: User's email address
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            role: User's role
            company_id: ID of the company the user belongs to
            **kwargs: Optional user attributes

        Returns:
            The created User object
        """
        user = User(
            email=email.lower(),
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            date_of_birth=date_of_birth,
            occupation=occupation,
            company_name=company_name,
            abn=abn,
            tfn=tfn,
            personal_email=personal_email,
            bsb=bsb,
            bank_account_number=bank_account_number,
            bank_account_holder_name=bank_account_holder_name,
            role=role,
            company_id=company_id,
            is_active=True,
            is_first_login=is_first_login
        )
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def commit():
        """Commit the current transaction."""
        db.session.commit()
