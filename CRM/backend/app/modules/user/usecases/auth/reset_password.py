"""
Reset Password Use Case - Reset password using OTP
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.models import OTP
from app.modules.user.repositories import UserRepository, OTPRepository
from app.modules.user.utils import validate_password_strength


class ResetPasswordUseCase(BaseCommandUseCase):
    """
    Reset password using OTP.

    Business Rules:
    - Passwords must match
    - Password must meet strength requirements
    - OTP must be valid
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.otp_repo = OTPRepository()

    def execute(self, email: str, otp_code: str, new_password: str,
                confirm_password: str) -> UseCaseResult:
        if new_password != confirm_password:
            return UseCaseResult.fail('Passwords do not match', 'PASSWORD_MISMATCH')

        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            return UseCaseResult.fail(error, 'WEAK_PASSWORD')

        user = self.user_repo.find_by_email(email)
        if not user:
            return UseCaseResult.fail('Invalid email', 'INVALID_EMAIL')

        otp = self.otp_repo.find_valid_otp(user.id, otp_code, OTP.PURPOSE_PASSWORD_RESET)

        if not otp or not otp.is_valid():
            return UseCaseResult.fail('Invalid or expired OTP', 'INVALID_OTP')

        otp.mark_used()
        user.set_password(new_password)
        db.session.commit()

        return UseCaseResult.ok({'message': 'Password reset successfully'})
