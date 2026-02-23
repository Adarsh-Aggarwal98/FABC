"""
FormResponse Repository - Data Access Layer for FormResponse entities
"""
from typing import List
from app.common.repository import BaseRepository
from app.modules.forms.models.form_response import FormResponse


class FormResponseRepository(BaseRepository[FormResponse]):
    """Repository for FormResponse data access"""
    model = FormResponse

    def get_by_form_paginated(self, form_id: int, page: int = 1, per_page: int = 20):
        """Get paginated responses for a form"""
        return FormResponse.query.filter_by(form_id=form_id)\
            .order_by(FormResponse.submitted_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

    def get_by_service_request(self, service_request_id: str) -> List[FormResponse]:
        """Get all responses for a service request"""
        return FormResponse.query.filter_by(service_request_id=service_request_id).all()

    def get_by_user(self, user_id: str) -> List[FormResponse]:
        """Get all responses submitted by a user"""
        return FormResponse.query.filter_by(user_id=user_id)\
            .order_by(FormResponse.submitted_at.desc()).all()
