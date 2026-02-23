"""
Tag repository for data access operations.
"""
from typing import List, Optional
from app.common.repository import BaseRepository
from app.extensions import db
from ..models import ClientTag, user_tags


class TagRepository(BaseRepository[ClientTag]):
    model = ClientTag

    def get_by_company(self, company_id: str) -> List[ClientTag]:
        """Get all tags for a company"""
        return ClientTag.query.filter_by(company_id=company_id).order_by(ClientTag.name).all()

    def get_by_name_and_company(self, name: str, company_id: str) -> Optional[ClientTag]:
        """Get tag by name within a company"""
        return ClientTag.query.filter_by(name=name, company_id=company_id).first()

    def get_tags_for_user(self, user_id: str) -> List[ClientTag]:
        """Get all tags assigned to a user"""
        return ClientTag.query.join(user_tags).filter(user_tags.c.user_id == user_id).all()

    def assign_tag_to_user(self, tag: ClientTag, user_id: str) -> bool:
        """Assign a tag to a user"""
        from app.modules.user.models import User
        user = User.query.get(user_id)
        if not user:
            return False

        if user not in tag.users:
            tag.users.append(user)
            db.session.flush()
        return True

    def remove_tag_from_user(self, tag: ClientTag, user_id: str) -> bool:
        """Remove a tag from a user"""
        from app.modules.user.models import User
        user = User.query.get(user_id)
        if not user:
            return False

        if user in tag.users:
            tag.users.remove(user)
            db.session.flush()
        return True

    def get_users_by_tags(self, tag_ids: List[int], company_id: str):
        """Get all users that have any of the specified tags"""
        from app.modules.user.models import User
        return User.query.join(user_tags).filter(
            user_tags.c.tag_id.in_(tag_ids),
            User.company_id == company_id
        ).distinct().all()
