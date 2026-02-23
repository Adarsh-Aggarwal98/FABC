"""
Role Repository - Data Access Layer
====================================

Repository for Role entity with custom queries.
Note: This is in the company module for convenience but operates on Role model.
"""
from typing import Optional
from app.common.repository import BaseRepository
from app.modules.user.models import Role


class RoleRepository(BaseRepository[Role]):
    """Repository with custom Role queries"""
    model = Role

    def find_by_name(self, name: str) -> Optional[Role]:
        """Find role by name"""
        return self.find_by(name=name)
