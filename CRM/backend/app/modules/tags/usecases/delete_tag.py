"""
Delete tag use case.
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from ..repositories import TagRepository


class DeleteTagUseCase(BaseCommandUseCase):
    """Delete a tag"""

    def __init__(self):
        self.tag_repo = TagRepository()

    def execute(self, tag_id: int, company_id: str) -> UseCaseResult:
        tag = self.tag_repo.get_by_id(tag_id)

        if not tag:
            return UseCaseResult.fail('Tag not found', 'NOT_FOUND')

        if tag.company_id != company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        self.tag_repo.delete(tag)
        self.tag_repo.save()

        return UseCaseResult.ok({'message': 'Tag deleted successfully'})
