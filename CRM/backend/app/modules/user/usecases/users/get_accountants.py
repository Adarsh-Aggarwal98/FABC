"""
Get Accountants Use Case - Get all active accountants
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.user.repositories import UserRepository


class GetAccountantsUseCase(BaseQueryUseCase):
    """Get all active accountants"""

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, company_id: str = None) -> UseCaseResult:
        accountants = self.user_repo.get_accountants(company_id=company_id)
        return UseCaseResult.ok({
            'accountants': [a.to_dict() for a in accountants]
        })
