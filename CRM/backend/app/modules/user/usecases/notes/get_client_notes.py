"""
Get Client Notes Use Case - Get notes for a client user
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.user.repositories import UserRepository, ClientNoteRepository


class GetClientNotesUseCase(BaseQueryUseCase):
    """Get notes for a client user"""

    def __init__(self):
        self.note_repo = ClientNoteRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str, page: int = 1, per_page: int = 20) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        pagination = self.note_repo.get_notes_for_user(user_id, page, per_page)

        return UseCaseResult.ok({
            'notes': [n.to_dict() for n in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
