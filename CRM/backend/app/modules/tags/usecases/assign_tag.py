"""
Assign tag to user use case.
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from ..repositories import TagRepository


class AssignTagToUserUseCase(BaseCommandUseCase):
    """
    Assign a tag to a user (client).

    Business Rules:
    - Tag must belong to the same company as the user
    - User must be a client (user role)
    """

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

        if user.company_id != company_id:
            return UseCaseResult.fail('User does not belong to your company', 'FORBIDDEN')

        success = self.tag_repo.assign_tag_to_user(tag, user_id)
        if not success:
            return UseCaseResult.fail('Failed to assign tag', 'OPERATION_FAILED')

        self.tag_repo.save()

        return UseCaseResult.ok({
            'message': 'Tag assigned successfully',
            'user_tags': [t.to_dict() for t in self.tag_repo.get_tags_for_user(user_id)]
        })
