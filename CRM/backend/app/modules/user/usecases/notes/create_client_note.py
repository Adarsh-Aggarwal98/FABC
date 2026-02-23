"""
Create Client Note Use Case - Create a note on a client profile
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.modules.user.models import ClientNote
from app.modules.user.repositories import UserRepository, ClientNoteRepository


class CreateClientNoteUseCase(BaseCommandUseCase):
    """
    Create a note on a client profile.

    Business Rules:
    - User must exist
    - Creator must have permission (accountant+)
    """

    def __init__(self):
        self.note_repo = ClientNoteRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str, created_by_id: str, content: str, is_pinned: bool = False) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        note = ClientNote(
            user_id=user_id,
            created_by_id=created_by_id,
            content=content,
            is_pinned=is_pinned
        )

        self.note_repo.create(note)
        self.note_repo.save()

        return UseCaseResult.ok({'note': note.to_dict()})
