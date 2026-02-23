"""
List tags use case.
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from ..repositories import TagRepository


class ListTagsUseCase(BaseQueryUseCase):
    """List all tags for a company"""

    def __init__(self):
        self.tag_repo = TagRepository()

    def execute(self, company_id: str) -> UseCaseResult:
        tags = self.tag_repo.get_by_company(company_id)
        return UseCaseResult.ok({
            'tags': [tag.to_dict() for tag in tags]
        })
