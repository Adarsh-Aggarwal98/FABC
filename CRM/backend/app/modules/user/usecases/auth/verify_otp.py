"""
Verify OTP Use Case - Verify OTP and issue tokens
"""
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.models import OTP
from app.modules.user.repositories import UserRepository, OTPRepository


class VerifyOTPUseCase(BaseCommandUseCase):
    """
    Step 2 of login: Verify OTP and issue tokens.

    Business Rules:
    - OTP must be valid and not expired
    - OTP is marked as used after verification
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.otp_repo = OTPRepository()

    def execute(self, email: str, otp_code: str) -> UseCaseResult:
        user = self.user_repo.find_by_email(email)

        if not user:
            return UseCaseResult.fail('Invalid email', 'INVALID_EMAIL')

        # Find valid OTP
        otp = self.otp_repo.find_valid_otp(user.id, otp_code, OTP.PURPOSE_LOGIN)

        if not otp or not otp.is_valid():
            return UseCaseResult.fail('Invalid or expired OTP', 'INVALID_OTP')

        # Mark OTP as used
        otp.mark_used()

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return UseCaseResult.ok({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_sensitive=True),
            'is_first_login': user.is_first_login
        })
