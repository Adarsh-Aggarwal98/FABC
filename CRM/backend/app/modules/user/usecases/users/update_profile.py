"""
Update Profile Use Case - Update user profile information
"""
from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.repositories import UserRepository


class UpdateProfileUseCase(BaseCommandUseCase):
    """Update user profile information"""

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, user_id: str, data: dict) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        for field in ['first_name', 'last_name', 'phone', 'address', 'company_name',
                      'personal_email', 'date_of_birth', 'occupation', 'visa_status',
                      'id_document_url', 'passport_url', 'bank_statement_url', 'driving_licence_url']:
            if field in data and data[field] is not None:
                setattr(user, field, data[field])

        db.session.commit()
        return UseCaseResult.ok({'user': user.to_dict()})
