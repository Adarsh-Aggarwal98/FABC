"""
ClientNote Repository - Data access for ClientNote entity
"""
from typing import List
from app.common.repository import BaseRepository
from app.modules.user.models import ClientNote


class ClientNoteRepository(BaseRepository[ClientNote]):
    """Repository for ClientNote data access"""
    model = ClientNote

    def get_notes_for_user(self, user_id: str, page: int = 1, per_page: int = 20):
        """Get paginated notes for a user, pinned first"""
        query = ClientNote.query.filter_by(user_id=user_id).order_by(
            ClientNote.is_pinned.desc(),
            ClientNote.created_at.desc()
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_pinned_notes(self, user_id: str) -> List[ClientNote]:
        """Get all pinned notes for a user"""
        return ClientNote.query.filter_by(
            user_id=user_id,
            is_pinned=True
        ).order_by(ClientNote.created_at.desc()).all()
