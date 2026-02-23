"""
Update tag use case.
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from ..repositories import TagRepository


class UpdateTagUseCase(BaseCommandUseCase):
    """Update an existing tag"""

    def __init__(self):
        self.tag_repo = TagRepository()

    def execute(self, tag_id: int, company_id: str, data: dict) -> UseCaseResult:
        tag = self.tag_repo.get_by_id(tag_id)

        if not tag:
            return UseCaseResult.fail('Tag not found', 'NOT_FOUND')

        if tag.company_id != company_id:
            return UseCaseResult.fail('Access denied', 'FORBIDDEN')

        # Check for duplicate name if changing name
        if 'name' in data and data['name'] != tag.name:
            existing = self.tag_repo.get_by_name_and_company(data['name'], company_id)
            if existing:
                return UseCaseResult.fail('A tag with this name already exists', 'TAG_EXISTS')
            tag.name = data['name']

        if 'color' in data:
            tag.color = data['color']

        self.tag_repo.save()

        return UseCaseResult.ok({'tag': tag.to_dict()})
