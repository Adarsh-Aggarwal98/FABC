"""
Change Password Use Case - Change user password
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.repositories import UserRepository
from app.modules.user.utils import validate_password_strength


class ChangePasswordUseCase(BaseCommandUseCase):
    """
    Change user password.

    Business Rules:
    - Current password must be correct
    - New passwords must match
    - New password must meet requirements
    """

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, user_id: str, current_password: str, new_password: str,
                confirm_password: str) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not user.check_password(current_password):
            return UseCaseResult.fail('Current password is incorrect', 'INVALID_PASSWORD')

        if new_password != confirm_password:
            return UseCaseResult.fail('Passwords do not match', 'PASSWORD_MISMATCH')

        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            return UseCaseResult.fail(error, 'WEAK_PASSWORD')

        user.set_password(new_password)
        db.session.commit()

        return UseCaseResult.ok({'message': 'Password updated successfully'})
