"""
Get Available Import Types Use Case

Handles retrieving the list of available import types for a user.
"""
import logging
from typing import List

from app.modules.imports.models import ImportType
from app.modules.imports.schemas import get_all_import_types

logger = logging.getLogger(__name__)


class GetAvailableTypesUseCase:
    """Use case for getting available import types."""

    @staticmethod
    def execute(is_super_admin: bool = False) -> List[ImportType]:
        """
        Get available import types for a user.

        Args:
            is_super_admin: Whether the user is a super admin

        Returns:
            List of ImportType objects available to the user
        """
        logger.debug(f"Getting available import types (is_super_admin={is_super_admin})")
        return get_all_import_types(is_super_admin)
