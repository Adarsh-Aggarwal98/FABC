"""
Create tag use case.
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from ..models import ClientTag
from ..repositories import TagRepository


class CreateTagUseCase(BaseCommandUseCase):
    """
    Create a new tag for a company.

    Business Rules:
    - Tag name must be unique within the company
    - Only admin+ can create tags
    """

    def __init__(self):
        self.tag_repo = TagRepository()

    def execute(self, company_id: str, name: str, color: str = '#3B82F6') -> UseCaseResult:
        # Check for duplicate
        existing = self.tag_repo.get_by_name_and_company(name, company_id)
        if existing:
            return UseCaseResult.fail('A tag with this name already exists', 'TAG_EXISTS')

        tag = ClientTag(
            name=name,
            color=color,
            company_id=company_id
        )

        self.tag_repo.create(tag)
        self.tag_repo.save()

        return UseCaseResult.ok({'tag': tag.to_dict()})
