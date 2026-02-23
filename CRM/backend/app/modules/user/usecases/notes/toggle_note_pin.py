"""
Toggle Note Pin Use Case - Toggle pin status of a note
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.modules.user.repositories import ClientNoteRepository


class ToggleNotePinUseCase(BaseCommandUseCase):
    """Toggle pin status of a note"""

    def __init__(self):
        self.note_repo = ClientNoteRepository()

    def execute(self, note_id: int) -> UseCaseResult:
        note = self.note_repo.get_by_id(note_id)
        if not note:
            return UseCaseResult.fail('Note not found', 'NOT_FOUND')

        note.is_pinned = not note.is_pinned
        self.note_repo.save()

        return UseCaseResult.ok({'note': note.to_dict()})
