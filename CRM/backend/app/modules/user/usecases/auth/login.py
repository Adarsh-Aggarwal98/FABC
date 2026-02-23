"""
Login Use Case - Validate credentials and send OTP if 2FA enabled
"""
from datetime import datetime
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.models import User, OTP
from app.modules.user.repositories import UserRepository, OTPRepository


class LoginUseCase(BaseCommandUseCase):
    """
    Step 1 of login: Validate credentials and send OTP if 2FA enabled.

    Business Rules:
    - User must exist and be active
    - Password must match
    - If 2FA enabled, send OTP
    - If 2FA disabled, return tokens directly
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.otp_repo = OTPRepository()

    def execute(self, email: str, password: str) -> UseCaseResult:
        user = self.user_repo.find_by_email(email)

        if not user or not user.check_password(password):
            return UseCaseResult.fail('Invalid email or password', 'INVALID_CREDENTIALS')

        if not user.is_active:
            return UseCaseResult.fail('Your account has been deactivated', 'ACCOUNT_INACTIVE')

        # If 2FA is disabled, directly return tokens
        if not user.two_fa_enabled:
            user.last_login = datetime.utcnow()
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return UseCaseResult.ok({
                'requires_2fa': False,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(include_sensitive=True),
                'is_first_login': user.is_first_login
            })

        # Generate and send OTP
        otp = OTP.create_otp(user.id, OTP.PURPOSE_LOGIN)

        # Send OTP via email
        self._send_otp_email(user, otp.code)

        return UseCaseResult.ok({
            'requires_2fa': True,
            'email': user.email,
            'message': 'OTP sent to your email'
        })

    def _send_otp_email(self, user: User, code: str):
        """Send OTP email"""
        # Log OTP to console for development
        current_app.logger.info(f'========== LOGIN OTP ==========')
        current_app.logger.info(f'User: {user.email}')
        current_app.logger.info(f'OTP Code: {code}')
        current_app.logger.info(f'================================')
        print(f'\n========== LOGIN OTP ==========')
        print(f'User: {user.email}')
        print(f'OTP Code: {code}')
        print(f'================================\n')

        try:
            from app.modules.notifications.services import NotificationService
            NotificationService.send_otp_email(user, code)
        except Exception as e:
            current_app.logger.error(f'Failed to send OTP email: {str(e)}')
