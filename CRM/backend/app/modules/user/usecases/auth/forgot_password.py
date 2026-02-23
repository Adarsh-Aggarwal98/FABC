"""
Forgot Password Use Case - Send password reset OTP
"""
from flask import current_app

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.modules.user.models import User, OTP
from app.modules.user.repositories import UserRepository


class ForgotPasswordUseCase(BaseCommandUseCase):
    """
    Send password reset OTP.

    Business Rules:
    - Don't reveal if email exists (security)
    - Send OTP if user exists
    """

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, email: str) -> UseCaseResult:
        user = self.user_repo.find_by_email(email)

        if not user:
            # Don't reveal if email exists
            return UseCaseResult.ok({'message': 'If the email exists, an OTP has been sent'})

        otp = OTP.create_otp(user.id, OTP.PURPOSE_PASSWORD_RESET)

        self._send_reset_email(user, otp.code)

        return UseCaseResult.ok({'message': 'If the email exists, an OTP has been sent'})

    def _send_reset_email(self, user: User, code: str):
        """Send password reset email"""
        # Log OTP to console for development
        current_app.logger.info(f'======= PASSWORD RESET OTP =======')
        current_app.logger.info(f'User: {user.email}')
        current_app.logger.info(f'OTP Code: {code}')
        current_app.logger.info(f'==================================')
        print(f'\n======= PASSWORD RESET OTP =======')
        print(f'User: {user.email}')
        print(f'OTP Code: {code}')
        print(f'==================================\n')

        try:
            from app.modules.notifications.services import NotificationService
            NotificationService.send_password_reset_email(user, code)
        except Exception as e:
            current_app.logger.error(f'Failed to send reset email: {str(e)}')
