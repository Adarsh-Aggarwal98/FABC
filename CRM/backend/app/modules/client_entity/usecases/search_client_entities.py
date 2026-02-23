"""
Search Client Entities Use Case
================================
Business logic for searching ClientEntities.
"""

from ..repositories import ClientEntityRepository
from .result import UseCaseResult


class SearchClientEntitiesUseCase:
    """Use case for searching ClientEntities."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()

    def execute(
        self,
        company_id: str,
        query: str,
        entity_type: str = None,
        is_active: bool = None,
        page: int = 1,
        per_page: int = 20
    ) -> UseCaseResult:
        """Search client entities."""
        try:
            entities, total = self.entity_repo.search(
                company_id=company_id,
                query_str=query,
                entity_type=entity_type,
                is_active=is_active,
                page=page,
                per_page=per_page
            )

            return UseCaseResult.ok({
                'entities': [e.to_dict(include_primary_contact=True) for e in entities],
                'total': total,
                'page': page,
                'per_page': per_page
            })

        except Exception as e:
            return UseCaseResult.fail(str(e), 'SEARCH_ERROR')
