"""
Get User Use Case - Get user by ID
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.user.repositories import UserRepository


class GetUserUseCase(BaseQueryUseCase):
    """Get user by ID"""

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, user_id: str, include_sensitive: bool = False) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')
        return UseCaseResult.ok({'user': user.to_dict(include_sensitive=include_sensitive)})
