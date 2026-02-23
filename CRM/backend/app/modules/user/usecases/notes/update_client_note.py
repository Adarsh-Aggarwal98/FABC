"""
Update Client Note Use Case - Update a client note
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.modules.user.repositories import ClientNoteRepository


class UpdateClientNoteUseCase(BaseCommandUseCase):
    """Update a client note"""

    def __init__(self):
        self.note_repo = ClientNoteRepository()

    def execute(self, note_id: int, data: dict, updated_by_id: str) -> UseCaseResult:
        note = self.note_repo.get_by_id(note_id)
        if not note:
            return UseCaseResult.fail('Note not found', 'NOT_FOUND')

        # Only creator can update their notes (or admins - handled at route level)
        if 'content' in data:
            note.content = data['content']
        if 'is_pinned' in data:
            note.is_pinned = data['is_pinned']

        self.note_repo.save()

        return UseCaseResult.ok({'note': note.to_dict()})
