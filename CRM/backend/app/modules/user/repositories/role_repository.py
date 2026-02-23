"""
Role Repository - Data access for Role entity
"""
from typing import Optional, List
from app.common.repository import BaseRepository
from app.modules.user.models import Role


class RoleRepository(BaseRepository[Role]):
    """Repository for Role data access"""
    model = Role

    def find_by_name(self, name: str) -> Optional[Role]:
        """Find role by name"""
        return Role.query.filter_by(name=name).first()

    def get_default_roles(self) -> List[Role]:
        """Get all default roles"""
        return Role.query.all()
