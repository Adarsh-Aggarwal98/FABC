"""
Toggle User Status Use Case - Activate or deactivate a user
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.repositories import UserRepository


class ToggleUserStatusUseCase(BaseCommandUseCase):
    """Activate or deactivate a user"""

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, user_id: str, is_active: bool) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        user.is_active = is_active
        db.session.commit()

        return UseCaseResult.ok({
            'user': user.to_dict(),
            'message': f'User {"activated" if is_active else "deactivated"} successfully'
        })
