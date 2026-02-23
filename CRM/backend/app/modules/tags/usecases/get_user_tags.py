"""
Get user tags use case.
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from ..repositories import TagRepository


class GetUserTagsUseCase(BaseQueryUseCase):
    """Get all tags for a specific user"""

    def __init__(self):
        self.tag_repo = TagRepository()

    def execute(self, user_id: str) -> UseCaseResult:
        tags = self.tag_repo.get_tags_for_user(user_id)
        return UseCaseResult.ok({
            'tags': [tag.to_dict() for tag in tags]
        })
