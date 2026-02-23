"""
Delete Client Note Use Case - Delete a client note
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.modules.user.repositories import ClientNoteRepository


class DeleteClientNoteUseCase(BaseCommandUseCase):
    """Delete a client note"""

    def __init__(self):
        self.note_repo = ClientNoteRepository()

    def execute(self, note_id: int) -> UseCaseResult:
        note = self.note_repo.get_by_id(note_id)
        if not note:
            return UseCaseResult.fail('Note not found', 'NOT_FOUND')

        self.note_repo.delete(note)
        self.note_repo.save()

        return UseCaseResult.ok({'message': 'Note deleted successfully'})
