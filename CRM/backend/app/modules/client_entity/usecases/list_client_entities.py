"""
List Client Entities Use Case
==============================
Business logic for listing ClientEntities.
"""

from ..repositories import ClientEntityRepository
from .result import UseCaseResult


class ListClientEntitiesUseCase:
    """Use case for listing ClientEntities."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()

    def execute(
        self,
        company_id: str,
        entity_type: str = None,
        is_active: bool = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'name',
        sort_order: str = 'asc'
    ) -> UseCaseResult:
        """List client entities for a company."""
        try:
            entities, total = self.entity_repo.list_by_company(
                company_id=company_id,
                entity_type=entity_type,
                is_active=is_active,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order
            )

            return UseCaseResult.ok({
                'entities': [e.to_dict(include_primary_contact=True) for e in entities],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            })

        except Exception as e:
            return UseCaseResult.fail(str(e), 'LIST_ERROR')
