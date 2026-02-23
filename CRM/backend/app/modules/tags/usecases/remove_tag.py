"""
Remove tag from user use case.
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from ..repositories import TagRepository


class RemoveTagFromUserUseCase(BaseCommandUseCase):
    """Remove a tag from a user"""

    def __init__(self):
        self.tag_repo = TagRepository()

    def execute(self, user_id: str, tag_id: int, company_id: str) -> UseCaseResult:
        from app.modules.user.models import User

        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            return UseCaseResult.fail('Tag not found', 'NOT_FOUND')

        if tag.company_id != company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        success = self.tag_repo.remove_tag_from_user(tag, user_id)
        if not success:
            return UseCaseResult.fail('Failed to remove tag', 'OPERATION_FAILED')

        self.tag_repo.save()

        return UseCaseResult.ok({
            'message': 'Tag removed successfully',
            'user_tags': [t.to_dict() for t in self.tag_repo.get_tags_for_user(user_id)]
        })
