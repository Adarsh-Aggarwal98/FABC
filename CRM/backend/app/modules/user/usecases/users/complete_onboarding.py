"""
Complete Onboarding Use Case - Complete first-time onboarding
"""
from datetime import datetime
from flask import current_app

from app.common.usecase import BaseCommandUseCase, UseCaseResult
from app.extensions import db
from app.modules.user.models import User
from app.modules.user.repositories import UserRepository
from app.modules.user.utils import validate_password_strength


class CompleteOnboardingUseCase(BaseCommandUseCase):
    """
    Complete first-time onboarding.

    Business Rules:
    - User must be in first login state
    - Passwords must match and meet requirements
    - All required personal information must be provided
    - Terms must be accepted
    - Creates service requests if selected
    """

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, user_id: str, data: dict) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if not user.is_first_login:
            return UseCaseResult.fail('Onboarding already completed', 'ALREADY_COMPLETED')

        # Validate password
        if data.get('new_password') != data.get('confirm_password'):
            return UseCaseResult.fail('Passwords do not match', 'PASSWORD_MISMATCH')

        if data.get('new_password'):
            is_valid, error = validate_password_strength(data['new_password'])
            if not is_valid:
                return UseCaseResult.fail(error, 'WEAK_PASSWORD')
            user.set_password(data['new_password'])

        # Validate terms acceptance
        if not data.get('terms_accepted'):
            return UseCaseResult.fail('Terms and conditions must be accepted', 'TERMS_NOT_ACCEPTED')

        # Update personal information
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'personal_email' in data:
            user.personal_email = data['personal_email']
        if 'address' in data:
            user.address = data['address']
        if 'company_name' in data:
            user.company_name = data['company_name']
        if 'visa_status' in data:
            user.visa_status = data['visa_status']

        # Update additional details (Australia-specific)
        if 'tfn' in data:
            user.tfn = data['tfn']
        if 'date_of_birth' in data:
            user.date_of_birth = data['date_of_birth']
        if 'occupation' in data:
            user.occupation = data['occupation']

        # Update bank account details
        if 'bsb' in data:
            user.bsb = data['bsb']
        if 'bank_account_number' in data:
            user.bank_account_number = data['bank_account_number']
        if 'bank_account_holder_name' in data:
            user.bank_account_holder_name = data['bank_account_holder_name']

        # Update document URLs (uploaded separately)
        if 'passport_url' in data:
            user.passport_url = data['passport_url']
        if 'bank_statement_url' in data:
            user.bank_statement_url = data['bank_statement_url']
        if 'driving_licence_url' in data:
            user.driving_licence_url = data['driving_licence_url']

        # Mark terms accepted
        user.terms_accepted = True
        user.terms_accepted_at = datetime.utcnow()

        # Mark onboarding complete
        user.is_first_login = False
        user.is_verified = True

        db.session.commit()

        # Create service requests
        if data.get('service_ids'):
            self._create_service_requests(user, data['service_ids'])

        return UseCaseResult.ok({'user': user.to_dict()})

    def _create_service_requests(self, user: User, service_ids: list):
        """Create service requests for selected services"""
        try:
            from app.modules.services.services import ServiceRequestService
            ServiceRequestService.create_requests_for_user(user, service_ids)
        except Exception as e:
            current_app.logger.error(f'Failed to create service requests: {str(e)}')
