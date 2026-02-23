"""
Invite User Use Case - Invite a new user
"""
from flask import current_app

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.models import User
from app.modules.user.repositories import UserRepository, RoleRepository
from app.modules.user.utils import generate_password


class InviteUserUseCase(BaseCommandUseCase):
    """
    Invite a new user.

    Business Rules:
    - Email must not exist
    - Role must be valid
    - Generates random password
    - Sends invitation email
    - Enforces plan limits for non-super_admin invitations
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()

    def execute(self, email: str, role_name: str, invited_by_id: str,
                first_name: str = None, last_name: str = None,
                company_id: str = None, supervisor_id: str = None) -> UseCaseResult:
        email = email.lower().strip()
        current_app.logger.info(f'[InviteUser] Starting invite for email: {email}, role: {role_name}')

        # Check if user already exists
        if self.user_repo.email_exists(email):
            current_app.logger.warning(f'[InviteUser] Email already exists: {email}')
            return UseCaseResult.fail('User with this email already exists', 'EMAIL_EXISTS')

        # Get role
        role = self.role_repo.find_by_name(role_name)
        if not role:
            current_app.logger.error(f'[InviteUser] Invalid role: {role_name}')
            return UseCaseResult.fail(f'Invalid role: {role_name}', 'INVALID_ROLE')

        current_app.logger.info(f'[InviteUser] Found role: {role.name} (id: {role.id})')

        # Enforce plan limits if company_id is provided
        if company_id:
            from app.modules.company.services import PlanLimitService
            can_add, error_msg = PlanLimitService.can_add_user(company_id, role_name)
            if not can_add:
                current_app.logger.warning(f'[InviteUser] Plan limit exceeded: {error_msg}')
                return UseCaseResult.fail(error_msg, 'PLAN_LIMIT_EXCEEDED')

        # Generate password
        password = generate_password()

        # Validate supervisor_id if provided
        if supervisor_id:
            supervisor = self.user_repo.get_by_id(supervisor_id)
            if not supervisor:
                return UseCaseResult.fail('Supervisor not found', 'NOT_FOUND')
            if supervisor.role.name != 'senior_accountant':
                return UseCaseResult.fail('Supervisor must be a senior accountant', 'INVALID_ROLE')
            # Only accountants can have supervisors
            if role_name != 'accountant':
                supervisor_id = None

        try:
            # Create user
            current_app.logger.info(f'[InviteUser] Creating user object...')
            user = User(
                email=email,
                role_id=role.id,
                first_name=first_name,
                last_name=last_name,
                invited_by_id=invited_by_id,
                company_id=company_id,
                supervisor_id=supervisor_id,
                is_first_login=True,
                is_active=True
            )
            user.set_password(password)

            self.user_repo.create(user)
            current_app.logger.info(f'[InviteUser] User added to session, committing...')
            db.session.commit()
            current_app.logger.info(f'[InviteUser] User committed successfully, id: {user.id}')

            # Build response dict using the role we already have (avoid lazy load issues)
            user_dict = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role.name,
                'company_id': user.company_id,
                'is_active': user.is_active,
                'is_first_login': user.is_first_login,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'[InviteUser] Database error: {str(e)}')
            current_app.logger.exception('[InviteUser] Full traceback:')
            return UseCaseResult.fail(f'Database error: {str(e)}', 'DATABASE_ERROR')

        # Send invite email (outside try block - user is created even if email fails)
        current_app.logger.info(f'[InviteUser] Sending invite email to {email}...')
        email_sent = self._send_invite_email(user, password)

        if email_sent:
            current_app.logger.info(f'[InviteUser] Invite complete for {email} - email sent successfully')
        else:
            current_app.logger.warning(f'[InviteUser] User {email} created but email could not be sent')

        return UseCaseResult.ok({
            'user': user_dict,
            'temp_password': password,
            'email_sent': email_sent,
            'message': 'User created successfully' + (' and invitation email sent' if email_sent else ' but invitation email could not be sent. Please share credentials manually.')
        })

    def _send_invite_email(self, user: User, password: str) -> bool:
        """Send invitation email. Returns True if sent, False if failed."""
        try:
            from app.modules.notifications.services import NotificationService
            NotificationService.send_invite_email(user, password)
            return True
        except Exception as e:
            current_app.logger.error(f'[InviteUser] Failed to send invite email: {str(e)}')
            return False
