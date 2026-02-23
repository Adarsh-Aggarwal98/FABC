"""
List Users Use Case - List users with pagination
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.user.repositories import UserRepository


class ListUsersUseCase(BaseQueryUseCase):
    """List users with pagination"""

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, role_filter: str = None, page: int = 1,
                per_page: int = 20, company_id: str = None, name_search: str = None) -> UseCaseResult:
        pagination = self.user_repo.get_users_paginated(role_filter, page, per_page, company_id, name_search)

        return UseCaseResult.ok({
            'users': [u.to_dict() for u in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
